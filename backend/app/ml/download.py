import tempfile
import urllib.request
from pathlib import Path

from .manifest import sha256_file


class ModelFileError(Exception):
    pass


def fetch_verified(path: Path, url: str, sha256: str, opener=urllib.request.urlopen) -> Path:
    path = Path(path)
    if path.is_file() and sha256_file(path) == sha256:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".part", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with opener(url, timeout=60) as response, tmp_path.open("wb") as out:
            while chunk := response.read(1 << 20):
                out.write(chunk)
        if sha256_file(tmp_path) != sha256:
            raise ModelFileError(f"downloaded {path.name} checksum mismatch")
        tmp_path.replace(path)
    except OSError as error:
        raise ModelFileError(f"download failed: {error}") from None
    finally:
        tmp_path.unlink(missing_ok=True)
    return path
