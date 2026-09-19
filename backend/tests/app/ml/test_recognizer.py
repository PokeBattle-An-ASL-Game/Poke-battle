import hashlib
import json

import pytest

from app.ml import recognizer as r
from app.ml.features import EXTRACTOR_VERSION, extractor_fingerprint

REGISTRY = {"HELLO": "hello"}


def write_model(tmp_path, artifact_format="stub"):
    (tmp_path / "model.bin").write_bytes(b"w")
    manifest = {
        "manifestVersion": 1, "modelVersion": "stub-v1", "artifactFormat": artifact_format,
        "extractorVersion": EXTRACTOR_VERSION, "extractorFingerprint": extractor_fingerprint(),
        "frameCount": 25, "labels": ["HELLO"], "qualifiedLabels": ["HELLO"],
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


def test_no_loaders_registered_by_default():
    assert r.LOADERS == {}
