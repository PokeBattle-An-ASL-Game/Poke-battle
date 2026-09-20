import hashlib
import json

import pytest

from app.config import Config, REPO_ROOT
from app.ml import manifest as m
from app.ml import wlasl_i3d as wlasl
from app.ml.features import EXTRACTOR_VERSION, extractor_fingerprint

REGISTRY = {"CITY": "city", "TABLE": "table", "NO": None}

EXPECTED_CLASS_MAP = {
    "82": "CITY",
    "28": "TABLE",
    "16": "YEAR",
    "22": "HOT",
    "53": "BIRD",
    "42": "KISS",
    "13": "NO",
    "77": "BASKETBALL",
    "49": "WHITE",
    "4": "CHAIR",
    "32": "BED",
    "38": "FISH",
    "65": "LAST",
    "71": "SECRETARY",
    "98": "TELL",
    "2": "COMPUTER",
    "21": "FINISH",
    "19": "BLACK",
    "80": "BUT",
    "1": "DRINK",
}


def write_model(tmp_path, weights=b"fake-weights", **overrides):
    (tmp_path / "model.bin").write_bytes(weights)
    data = {
        "manifestVersion": 1,
        "modelVersion": "test-v1",
        "artifactFormat": "test",
        "extractorVersion": EXTRACTOR_VERSION,
        "extractorFingerprint": extractor_fingerprint(),
        "frameCount": 25,
        "labels": ["CITY", "TABLE", "NO"],
        "qualifiedLabels": ["CITY", "NO"],
        "weightsFile": "model.bin",
        "weightsSha256": hashlib.sha256(b"fake-weights").hexdigest(),
        **overrides,
    }
    (tmp_path / m.MANIFEST_FILE).write_text(json.dumps(data))


def test_valid_manifest(tmp_path):
    write_model(tmp_path)
    manifest = m.load_manifest(tmp_path, REGISTRY)
    assert manifest.model_version == "test-v1"
    assert manifest.qualified_labels == {"CITY", "NO"}
    assert manifest.weights_path == tmp_path / "model.bin"


def test_missing_manifest(tmp_path):
    with pytest.raises(m.ManifestError, match="no model manifest"):
        m.load_manifest(tmp_path, REGISTRY)


@pytest.mark.parametrize(
    "overrides",
    [
        {"manifestVersion": 2},
        {"extractorVersion": "other-extractor"},
        {"extractorFingerprint": "0" * 64},
        {"frameCount": 24},
        {"frameCount": True},
        {"labels": ["CITY", "CITY"]},
        {"labels": ["CITY", "NOT_A_SIGN"]},
        {"labels": ["CITY", 5]},
        {"qualifiedLabels": ["TABLE", "WATER"]},
        {"weightsFile": "../model.bin"},
        {"weightsFile": "missing.bin"},
        {"weightsSha256": "0" * 64},
        {"modelVersion": None},
    ],
)
def test_invalid_manifest_rejected(tmp_path, overrides):
    write_model(tmp_path, **overrides)
    with pytest.raises(m.ManifestError):
        m.load_manifest(tmp_path, REGISTRY)


def test_wlasl_manifest_skips_landmark_checks(tmp_path):
    write_model(tmp_path, artifactFormat="wlasl-i3d", extractorVersion=None, extractorFingerprint=None,
                frameCount=64, numClasses=100)
    manifest = m.load_manifest(tmp_path, REGISTRY)
    assert manifest.artifact_format == "wlasl-i3d"
    assert manifest.settings["numClasses"] == 100


def test_other_formats_keep_landmark_checks(tmp_path):
    write_model(tmp_path, extractorVersion=None)
    with pytest.raises(m.ManifestError, match="extractorVersion"):
        m.load_manifest(tmp_path, REGISTRY)


def test_tampered_weights_rejected(tmp_path):
    write_model(tmp_path, weights=b"swapped")
    with pytest.raises(m.ManifestError, match="checksum"):
        m.load_manifest(tmp_path, REGISTRY)


def test_broken_json_rejected(tmp_path):
    (tmp_path / m.MANIFEST_FILE).write_text("{oops")
    with pytest.raises(m.ManifestError):
        m.load_manifest(tmp_path, REGISTRY)


def test_sign_qualification(tmp_path):
    write_model(tmp_path)
    manifest = m.load_manifest(tmp_path, REGISTRY)
    assert m.is_sign_qualified("CITY", REGISTRY, manifest)
    assert not m.is_sign_qualified("TABLE", REGISTRY, manifest)
    assert not m.is_sign_qualified("NO", REGISTRY, manifest)
    assert not m.is_sign_qualified("WATER", REGISTRY, manifest)


def _template_data():
    return json.loads(m.MANIFEST_TEMPLATE.read_text(encoding="utf-8"))


def test_committed_wlasl_template_matches_signs_and_class_map():
    data = _template_data()
    signs = json.loads((REPO_ROOT / "shared/signs.json").read_text(encoding="utf-8"))["signs"]
    sign_ids = [entry["id"] for entry in signs]
    assert data["labels"] == sign_ids
    assert data["qualifiedLabels"] == sign_ids
    assert set(data["labels"]) == set(EXPECTED_CLASS_MAP.values())
    assert data["classMap"] == EXPECTED_CLASS_MAP
    assert data["artifactFormat"] == "wlasl-i3d"
    assert data["preprocessingVersion"] == wlasl.PREPROCESSING_VERSION
    assert data["frameCount"] == 64
    assert data["numClasses"] == 100
    assert data["minProb"] == 0.25
    assert data["minMargin"] == 3.0
    assert data["weightsFile"] == "wlasl100_i3d.pt"
    assert data["weightsSha256"] == "a61d7dda5f875ce5ebd9d407c56874f77d1cd2aeb4bc7cd0d98a6e1ca4669a0c"
    assert data["modelVersion"] == "wlasl100-i3d-provisional-v1"


def test_installed_wlasl_template_loads_with_fake_weights(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "FRAME_COUNT", 64)
    weights = b"fake-wlasl-weights"
    sha = hashlib.sha256(weights).hexdigest()
    (tmp_path / "wlasl100_i3d.pt").write_bytes(weights)
    m.write_installed_manifest(tmp_path, weights_sha256=sha)

    registry = {entry["id"]: entry["modelLabel"] for entry in
                json.loads((REPO_ROOT / "shared/signs.json").read_text(encoding="utf-8"))["signs"]}
    manifest = m.load_manifest(tmp_path, registry)
    assert manifest.model_version == "wlasl100-i3d-provisional-v1"
    assert set(manifest.labels) == set(EXPECTED_CLASS_MAP.values())
    assert manifest.qualified_labels == frozenset(EXPECTED_CLASS_MAP.values())
    assert manifest.weights_path == tmp_path / "wlasl100_i3d.pt"

    class_to_sign, num_classes, min_prob, min_margin = wlasl.read_settings(manifest)
    assert num_classes == 100 and min_prob == 0.25 and min_margin == 3.0
    assert class_to_sign == {int(index): sign for index, sign in EXPECTED_CLASS_MAP.items()}
