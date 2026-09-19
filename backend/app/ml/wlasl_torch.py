import importlib.util
import pickle
import urllib.request
from pathlib import Path
from typing import Callable

import numpy as np
import torch

from ..config import REPO_ROOT
from .download import fetch_verified
from .manifest import sha256_file
from .recognizer import ModelNotReady

I3D_SOURCE_URL = (
    "https://raw.githubusercontent.com/dxli94/WLASL/"
    "ac00e6be631c1a2a486621b65f202219f3964d6b/code/I3D/pytorch_i3d.py"
)
I3D_SOURCE_SHA256 = "1b35b81b4dc8ea6ef55c87063515d058761fd25caf9381bad3dcc0ed5f3c3de5"
I3D_SOURCE_PATH = REPO_ROOT / "backend/app/ml/artifacts/wlasl/pytorch_i3d.py"
PRETRAINED_CLASSES = 400


def ensure_i3d_source(path: Path = I3D_SOURCE_PATH, opener=urllib.request.urlopen) -> Path:
    return fetch_verified(path, I3D_SOURCE_URL, I3D_SOURCE_SHA256, opener)


def _i3d_class(source_path: Path):
    source_path = Path(source_path)
    if not source_path.is_file() or sha256_file(source_path) != I3D_SOURCE_SHA256:
        raise ModelNotReady("wlasl model source missing or checksum mismatch")
    spec = importlib.util.spec_from_file_location("pookie_wlasl_pytorch_i3d", source_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.InceptionI3d


def load_i3d(weights_path: Path, num_classes: int, source_path: Path = I3D_SOURCE_PATH) -> Callable[[np.ndarray], np.ndarray]:
    model = _i3d_class(source_path)(PRETRAINED_CLASSES, in_channels=3)
    model.replace_logits(num_classes)
    try:
        model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    except (RuntimeError, pickle.UnpicklingError, OSError):
        raise ModelNotReady("wlasl weights do not fit the model") from None
    model.eval()

    def run(video: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            return model(torch.from_numpy(video)).numpy()

    return run


if __name__ == "__main__":
    print(ensure_i3d_source())
