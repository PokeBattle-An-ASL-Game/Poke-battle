import importlib.util
import pickle
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Callable

import numpy as np
import torch

from ..config import REPO_ROOT, Config
from .download import ModelFileError, fetch_verified
from .manifest import ManifestError, sha256_file, write_installed_manifest
from .recognizer import ModelNotReady


I3D_SOURCE_URL = (
    "https://raw.githubusercontent.com/dxli94/WLASL/"
    "ac00e6be631c1a2a486621b65f202219f3964d6b/code/I3D/pytorch_i3d.py"
)
I3D_SOURCE_SHA256 = "1b35b81b4dc8ea6ef55c87063515d058761fd25caf9381bad3dcc0ed5f3c3de5"
I3D_SOURCE_PATH = REPO_ROOT / "backend/app/ml/artifacts/wlasl/pytorch_i3d.py"
PRETRAINED_CLASSES = 400
CHECKPOINT_NAME = "wlasl100_i3d.pt"
CHECKPOINT_SHA256 = "a61d7dda5f875ce5ebd9d407c56874f77d1cd2aeb4bc7cd0d98a6e1ca4669a0c"


def ensure_i3d_source(path: Path = I3D_SOURCE_PATH, opener=urllib.request.urlopen) -> Path:
    return fetch_verified(path, I3D_SOURCE_URL, I3D_SOURCE_SHA256, opener)


def install_checkpoint(source: Path, model_dir: Path = Config.MODEL_DIR) -> Path:
    model_dir = Path(model_dir)
    target = model_dir / CHECKPOINT_NAME
    if not (target.is_file() and sha256_file(target) == CHECKPOINT_SHA256):
        model_dir.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(".part")
        try:
            shutil.copyfile(source, partial)
            if sha256_file(partial) != CHECKPOINT_SHA256:
                raise ModelFileError("checkpoint checksum mismatch; expected the WLASL100 I3D trial checkpoint")
            partial.replace(target)
        except OSError as error:
            raise ModelFileError(f"checkpoint copy failed: {error}") from None
        finally:
            partial.unlink(missing_ok=True)
    try:
        write_installed_manifest(model_dir, weights_sha256=CHECKPOINT_SHA256)
    except ManifestError as error:
        raise ModelFileError(str(error)) from None
    return target



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
    if len(sys.argv) > 1:
        print(install_checkpoint(Path(sys.argv[1])))
