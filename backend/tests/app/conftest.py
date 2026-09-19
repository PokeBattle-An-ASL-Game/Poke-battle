import io
import json
import uuid
from pathlib import Path

import pytest
from PIL import Image

from app import create_app
from app.config import Config
from app.ml.manifest import ModelManifest
from app.ml.recognizer import Prediction

FAKE_MANIFEST = ModelManifest("fake-v1", "fake", ("HELLO", "YES", "NO"), frozenset({"HELLO", "YES"}), Path("x"))


class FakeRecognizer:
    def __init__(self, prediction=None, error=None):
        self.prediction = prediction or Prediction("HELLO", 0.9, None, "fake-v1")
        self.error = error
        self.calls = 0

    def predict_sequence(self, frames_rgb, timestamps_ms):
        self.calls += 1
        if self.error:
            raise self.error
        return self.prediction


@pytest.fixture
def fake_recognizer():
    return FakeRecognizer


@pytest.fixture
def fake_manifest():
    return FAKE_MANIFEST


@pytest.fixture
def game_files(tmp_path):
    levels = tmp_path / "levels"
    levels.mkdir()
    for level_id, available, signs in ((1, True, ["HELLO", "YES"]), (2, False, ["HELLO", "YES"]), (3, True, ["NO", "YES"])):
        moves = [{"id": f"move-{i}", "signId": s} for i, s in enumerate(signs, 1)]
        (levels / f"level-{level_id}.json").write_text(json.dumps({"id": level_id, "available": available, "moves": moves}))
    signs_path = tmp_path / "signs.json"
    registry = [{"id": s, "modelLabel": None if s == "NO" else s.lower()} for s in ("HELLO", "YES", "NO")]
    signs_path.write_text(json.dumps({"schemaVersion": 1, "signs": registry}))
    return {"LEVELS_DIR": levels, "SIGNS_PATH": signs_path, "MODEL_DIR": tmp_path / "no-model"}


@pytest.fixture
def post_attempt(make_jpeg):
    def _post(client, frames=None, **fields):
        data = {"requestId": str(uuid.uuid4()), "levelId": "1", "moveId": "move-1",
                "timestampsMs": json.dumps([i * 100.0 for i in range(25)]), **fields}
        frames = frames if frames is not None else [make_jpeg()] * 25
        data["frames"] = [(io.BytesIO(f), f"f{i}.jpg", "image/jpeg") for i, f in enumerate(frames)]
        return client.post("/api/validate-sign", data=data, content_type="multipart/form-data")

    return _post


@pytest.fixture
def make_client(game_files):
    def _make(recognizer=None, manifest=FAKE_MANIFEST, **overrides):
        if recognizer is None and manifest is not None:
            recognizer = FakeRecognizer()
        app = create_app({**game_files, **overrides}, recognizer=recognizer, manifest=manifest)
        return app.test_client()

    return _make


@pytest.fixture
def config():
    return {key: getattr(Config, key) for key in dir(Config) if key.isupper()}


@pytest.fixture
def make_jpeg():
    def _make(width=64, height=48, color=(200, 120, 80)):
        buffer = io.BytesIO()
        Image.new("RGB", (width, height), color).save(buffer, format="JPEG")
        return buffer.getvalue()

    return _make
