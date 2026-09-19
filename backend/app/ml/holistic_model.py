import tempfile
import urllib.request
from pathlib import Path

from ..config import REPO_ROOT
from .features import LANDMARK_MODEL_SHA256
from .manifest import sha256_file

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/holistic_landmarker/"
    "holistic_landmarker/float16/1/holistic_landmarker.task"
)
DEFAULT_PATH = REPO_ROOT / "backend/app/ml/artifacts/mediapipe/holistic_landmarker.task"


class ModelFileError(Exception):
    pass


def ensure_model(path: Path = DEFAULT_PATH, url: str = MODEL_URL, opener=urllib.request.urlopen) -> Path:
    path = Path(path)
    if path.is_file() and sha256_file(path) == LANDMARK_MODEL_SHA256:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".part", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        with opener(url, timeout=60) as response, tmp_path.open("wb") as out:
            while chunk := response.read(1 << 20):
                out.write(chunk)
        if sha256_file(tmp_path) != LANDMARK_MODEL_SHA256:
            raise ModelFileError("downloaded landmark model checksum mismatch")
        tmp_path.replace(path)
    except OSError as error:
        raise ModelFileError(f"download failed: {error}") from None
    finally:
        tmp_path.unlink(missing_ok=True)
    return path


if __name__ == "__main__":
    print(ensure_model())
