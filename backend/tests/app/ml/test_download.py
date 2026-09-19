import hashlib
import io

import pytest

from app.ml import download as d

CONTENT = b"pretend model file"
SHA = hashlib.sha256(CONTENT).hexdigest()


def test_fetch_verified_downloads_to_path(tmp_path):
    target = tmp_path / "sub" / "file.bin"
    assert d.fetch_verified(target, "https://x", SHA, opener=lambda url, timeout: io.BytesIO(CONTENT)) == target
    assert target.read_bytes() == CONTENT


def test_fetch_verified_rejects_wrong_checksum_and_leaves_nothing(tmp_path):
    with pytest.raises(d.ModelFileError, match="file.bin checksum mismatch"):
        d.fetch_verified(tmp_path / "file.bin", "https://x", SHA, opener=lambda url, timeout: io.BytesIO(b"bad"))
    assert list(tmp_path.iterdir()) == []
