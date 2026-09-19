import hashlib
import json

import pytest

from app.ml import recognizer as r
from app.ml.features import EXTRACTOR_VERSION, extractor_fingerprint

REGISTRY = {"CITY": "city"}


def write_model(tmp_path, artifact_format="stub"):
    (tmp_path / "model.bin").write_bytes(b"w")
    manifest = {
        "manifestVersion": 1, "modelVersion": "stub-v1", "artifactFormat": artifact_format,
        "extractorVersion": EXTRACTOR_VERSION, "extractorFingerprint": extractor_fingerprint(),
        "frameCount": 25, "labels": ["CITY"], "qualifiedLabels": ["CITY"],
        "weightsFile": "model.bin", "weightsSha256": hashlib.sha256(b"w").hexdigest(),
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))


def test_no_model_directory_is_not_ready(tmp_path):
    with pytest.raises(r.ModelNotReady, match="no model manifest"):
        r.load_recognizer(tmp_path / "missing", REGISTRY)


def test_unknown_artifact_format_is_not_ready(tmp_path):
    write_model(tmp_path, artifact_format="mystery")
    with pytest.raises(r.ModelNotReady, match="unsupported artifact format"):
        r.load_recognizer(tmp_path, REGISTRY)


def test_registered_loader_is_used(tmp_path, monkeypatch):
    class Stub:
        def predict_sequence(self, frames_rgb, timestamps_ms):
            return r.Prediction(None, None, "uncertain_prediction", "stub-v1")

    monkeypatch.setitem(r.LOADERS, "stub", lambda manifest: Stub())
    write_model(tmp_path)
    recognizer, manifest = r.load_recognizer(tmp_path, REGISTRY)
    assert manifest.model_version == "stub-v1"
    assert recognizer.predict_sequence([], []).reason == "uncertain_prediction"


def test_only_wlasl_loader_registered_by_default():
    assert set(r.LOADERS) == {"wlasl-i3d"}


def test_wlasl_loader_is_used(tmp_path, monkeypatch):
    from app.ml import wlasl_i3d

    monkeypatch.setattr(wlasl_i3d, "load_wlasl_recognizer", lambda manifest: ("built", manifest.model_version))
    write_model(tmp_path, artifact_format="wlasl-i3d")
    recognizer, _ = r.load_recognizer(tmp_path, REGISTRY)
    assert recognizer == ("built", "stub-v1")


def test_missing_wlasl_runtime_is_not_ready(tmp_path, monkeypatch):
    from app.ml import wlasl_i3d

    def no_runtime(weights_path, num_classes):
        raise ModuleNotFoundError("torch")

    monkeypatch.setattr(wlasl_i3d, "read_settings", lambda manifest: ({}, 100, 0.25, 3.0))
    monkeypatch.setattr(wlasl_i3d, "build_model", no_runtime)
    write_model(tmp_path, artifact_format="wlasl-i3d")
    with pytest.raises(r.ModelNotReady, match="runtime not installed"):
        r.load_recognizer(tmp_path, REGISTRY)
