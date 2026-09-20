import hashlib
import io
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from app.ml import wlasl_torch as t  # noqa: E402
from app.ml.manifest import MANIFEST_FILE  # noqa: E402
from app.ml.recognizer import ModelNotReady  # noqa: E402

FAKE_SOURCE = b"""
from torch import nn

class InceptionI3d(nn.Module):
    def __init__(self, num_classes, in_channels=3):
        super().__init__()
        self.logits = nn.Conv3d(in_channels, num_classes, 1)
        self.dropout = nn.Dropout(0.9)

    def replace_logits(self, num_classes):
        self.logits = nn.Conv3d(self.logits.in_channels, num_classes, 1)

    def forward(self, x):
        return self.logits(self.dropout(x)).mean(dim=(3, 4))
"""


@pytest.fixture
def source(tmp_path, monkeypatch):
    path = tmp_path / "pytorch_i3d.py"
    path.write_bytes(FAKE_SOURCE)
    monkeypatch.setattr(t, "I3D_SOURCE_SHA256", hashlib.sha256(FAKE_SOURCE).hexdigest())
    return path


def save_weights(path, source, num_classes):
    model = t._i3d_class(source)(400, in_channels=3)
    model.replace_logits(num_classes)
    torch.save(model.state_dict(), path)
    return model.eval()


def test_load_i3d_runs_model_in_eval_mode(tmp_path, source):
    expected_model = save_weights(tmp_path / "w.pt", source, 5)
    run = t.load_i3d(tmp_path / "w.pt", 5, source)
    video = np.random.default_rng(0).uniform(-1, 1, (1, 3, 4, 8, 8)).astype(np.float32)
    out = run(video)
    assert isinstance(out, np.ndarray) and out.shape == (1, 5, 4)
    np.testing.assert_allclose(out, expected_model(torch.from_numpy(video)).detach().numpy(), rtol=1e-6)
    np.testing.assert_array_equal(out, run(video))


def test_source_with_wrong_checksum_is_never_run(tmp_path, source):
    source.write_bytes(b"raise SystemExit('should not run')")
    with pytest.raises(ModelNotReady, match="source"):
        t.load_i3d(tmp_path / "w.pt", 5, source)


def test_missing_source_is_not_ready(tmp_path):
    with pytest.raises(ModelNotReady, match="source"):
        t.load_i3d(tmp_path / "w.pt", 5, tmp_path / "missing.py")


@pytest.mark.parametrize("weights", ["other_classes", "garbage", "missing"])
def test_unusable_weights_are_not_ready(tmp_path, source, weights):
    path = tmp_path / "w.pt"
    if weights == "other_classes":
        save_weights(path, source, 7)
    elif weights == "garbage":
        path.write_bytes(b"not a checkpoint")
    with pytest.raises(ModelNotReady, match="weights"):
        t.load_i3d(path, 5, source)


def test_ensure_source_downloads_and_verifies(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "I3D_SOURCE_SHA256", hashlib.sha256(FAKE_SOURCE).hexdigest())
    target = tmp_path / "wlasl" / "pytorch_i3d.py"
    assert t.ensure_i3d_source(target, opener=lambda url, timeout: io.BytesIO(FAKE_SOURCE)) == target
    assert target.read_bytes() == FAKE_SOURCE


@pytest.mark.skipif(not t.I3D_SOURCE_PATH.is_file(), reason="run python -m app.ml.wlasl_torch first")
def test_pinned_wlasl_source_builds_i3d(tmp_path):
    model = t._i3d_class(t.I3D_SOURCE_PATH)(400, in_channels=3)
    model.replace_logits(100)
    torch.save(model.state_dict(), tmp_path / "w.pt")
    run = t.load_i3d(tmp_path / "w.pt", 100)
    assert run(np.zeros((1, 3, 16, 224, 224), np.float32)).shape[:2] == (1, 100)


@pytest.fixture
def checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "FINAL_nslt_100.pt"
    path.write_bytes(b"pretend checkpoint")
    monkeypatch.setattr(t, "CHECKPOINT_SHA256", hashlib.sha256(b"pretend checkpoint").hexdigest())
    return path


def test_install_checkpoint_copies_verified_file(tmp_path, checkpoint):
    model_dir = tmp_path / "model"
    target = t.install_checkpoint(checkpoint, model_dir)
    assert target == model_dir / "wlasl100_i3d.pt"
    assert target.read_bytes() == b"pretend checkpoint"
    manifest_path = model_dir / MANIFEST_FILE
    assert set(model_dir.iterdir()) == {target, manifest_path}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["weightsFile"] == "wlasl100_i3d.pt"
    assert data["weightsSha256"] == t.CHECKPOINT_SHA256
    assert data["modelVersion"] == "wlasl100-i3d-provisional-v1"
    assert len(data["labels"]) == 19 and data["labels"] == data["qualifiedLabels"]


def test_install_checkpoint_keeps_existing_valid_file(tmp_path, checkpoint):
    model_dir = tmp_path / "model"
    target = t.install_checkpoint(checkpoint, model_dir)
    checkpoint.unlink()
    (model_dir / MANIFEST_FILE).unlink()
    assert t.install_checkpoint(checkpoint, model_dir) == target
    assert (model_dir / MANIFEST_FILE).is_file()


def test_install_checkpoint_rejects_other_file(tmp_path, checkpoint):
    checkpoint.write_bytes(b"some other model")
    with pytest.raises(t.ModelFileError, match="checksum"):
        t.install_checkpoint(checkpoint, tmp_path / "model")
    assert list((tmp_path / "model").iterdir()) == []


def test_install_checkpoint_missing_source(tmp_path, checkpoint):
    with pytest.raises(t.ModelFileError, match="copy failed"):
        t.install_checkpoint(tmp_path / "nope.pt", tmp_path / "model")


def test_pinned_checkpoint_checksum_is_trial_checkpoint():
    assert t.CHECKPOINT_SHA256 == "a61d7dda5f875ce5ebd9d407c56874f77d1cd2aeb4bc7cd0d98a6e1ca4669a0c"
