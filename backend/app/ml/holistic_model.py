import urllib.request
from pathlib import Path

from ..config import REPO_ROOT
from .download import ModelFileError, fetch_verified
from .features import LANDMARK_MODEL_SHA256

__all__ = ["ModelFileError", "ensure_model"]

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/holistic_landmarker/"
    "holistic_landmarker/float16/1/holistic_landmarker.task"
)
DEFAULT_PATH = REPO_ROOT / "backend/app/ml/artifacts/mediapipe/holistic_landmarker.task"


def ensure_model(path: Path = DEFAULT_PATH, url: str = MODEL_URL, opener=urllib.request.urlopen) -> Path:
    return fetch_verified(path, url, LANDMARK_MODEL_SHA256, opener)


if __name__ == "__main__":
    print(ensure_model())
