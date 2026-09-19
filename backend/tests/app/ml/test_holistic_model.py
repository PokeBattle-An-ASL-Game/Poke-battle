import hashlib
import io

import pytest

from app.ml import holistic_model as h

CONTENT = b"pretend landmark model"


class FakeOpener:
    def __init__(self, content=CONTENT, error=None):
        self.content, self.error, self.calls = content, error, 0

    def __call__(self, url, timeout):
        self.calls += 1
        if self.error:
            raise self.error
        return io.BytesIO(self.content)


@pytest.fixture(autouse=True)
def pinned_checksum(monkeypatch):
    monkeypatch.setattr(h, "LANDMARK_MODEL_SHA256", hashlib.sha256(CONTENT).hexdigest())


def test_downloads_and_verifies(tmp_path):
    target = tmp_path / "models" / "holistic.task"
    assert h.ensure_model(target, opener=FakeOpener()) == target
    assert target.read_bytes() == CONTENT
    assert list(target.parent.iterdir()) == [target]


def test_existing_valid_file_is_not_downloaded_again(tmp_path):
    target = tmp_path / "holistic.task"
    target.write_bytes(CONTENT)
    opener = FakeOpener()
    h.ensure_model(target, opener=opener)
    assert opener.calls == 0


def test_corrupted_file_is_replaced(tmp_path):
    target = tmp_path / "holistic.task"
    target.write_bytes(b"corrupted")
    h.ensure_model(target, opener=FakeOpener())
    assert target.read_bytes() == CONTENT


def test_checksum_mismatch_leaves_nothing_behind(tmp_path):
    target = tmp_path / "holistic.task"
    with pytest.raises(h.ModelFileError, match="checksum"):
        h.ensure_model(target, opener=FakeOpener(content=b"tampered"))
    assert list(tmp_path.iterdir()) == []


def test_network_failure_leaves_nothing_behind(tmp_path):
    with pytest.raises(h.ModelFileError, match="download failed"):
        h.ensure_model(tmp_path / "holistic.task", opener=FakeOpener(error=OSError("offline")))
    assert list(tmp_path.iterdir()) == []


def test_url_is_pinned_to_version_one():
    assert "/float16/1/" in h.MODEL_URL and "latest" not in h.MODEL_URL
