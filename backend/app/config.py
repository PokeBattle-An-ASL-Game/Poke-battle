import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Config:
    LEVELS_DIR = Path(os.environ.get("POOKIE_LEVELS_DIR", REPO_ROOT / "frontend/src/constants/levels"))
    SIGNS_PATH = Path(os.environ.get("POOKIE_SIGNS_PATH", REPO_ROOT / "shared/signs.json"))
    MODEL_DIR = Path(os.environ.get("POOKIE_MODEL_DIR", REPO_ROOT / "backend/app/ml/artifacts"))
    CORS_ORIGINS = _origins(os.environ.get("POOKIE_CORS_ORIGINS", "http://localhost:5173"))

    LEVEL_IDS = range(1, 8)
    FRAME_COUNT = 25
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024
    MAX_FRAME_BYTES = 200 * 1024
    MAX_FRAME_WIDTH = 1280
    MAX_FRAME_HEIGHT = 720
    # Provisional; pending agreement with ML and frontend owners.
    MIN_SEQUENCE_SPAN_MS = 1000
    MAX_SEQUENCE_SPAN_MS = 5000
