import hashlib
import json

import pytest

from app.ml import manifest as m
from app.ml.features import EXTRACTOR_VERSION, extractor_fingerprint

REGISTRY = {"HELLO": "hello", "YES": "yes", "NO": None}


def write_model(tmp_path, weights=b"fake-weights", **overrides):
    (tmp_path / "model.bin").write_bytes(weights)
    data = {
        "manifestVersion": 1,
        "modelVersion": "test-v1",
        "artifactFormat": "test",
        "extractorVersion": EXTRACTOR_VERSION,
        "extractorFingerprint": extractor_fingerprint(),
        "frameCount": 25,
        "labels": ["HELLO", "YES", "NO"],
        "qualifiedLabels": ["HELLO", "NO"],
        "weightsFile": "model.bin",
        "weightsSha256": hashlib.sha256(b"fake-weights").hexdigest(),
        **overrides,
    }
    (tmp_path / m.MANIFEST_FILE).write_text(json.dumps(data))


def test_valid_manifest(tmp_path):
    write_model(tmp_path)
    manifest = m.load_manifest(tmp_path, REGISTRY)
    assert manifest.model_version == "test-v1"
    assert manifest.qualified_labels == {"HELLO", "NO"}
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
        {"labels": ["HELLO", "HELLO"]},
        {"labels": ["HELLO", "NOT_A_SIGN"]},
        {"labels": ["HELLO", 5]},
        {"qualifiedLabels": ["YES", "WATER"]},
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
    assert m.is_sign_qualified("HELLO", REGISTRY, manifest)
    assert not m.is_sign_qualified("YES", REGISTRY, manifest)
    assert not m.is_sign_qualified("NO", REGISTRY, manifest)
    assert not m.is_sign_qualified("WATER", REGISTRY, manifest)
