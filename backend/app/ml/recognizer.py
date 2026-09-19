from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol, Sequence

import numpy as np

from .manifest import ManifestError, ModelManifest, load_manifest


@dataclass(frozen=True)
class Prediction:
    """label is None when the model rejects the attempt; reason explains why."""

    label: str | None
    score: float | None
    reason: str | None
    model_version: str


class Recognizer(Protocol):
    def predict_sequence(self, frames_rgb: Sequence[np.ndarray], timestamps_ms: Sequence[float]) -> Prediction: ...


class ModelNotReady(Exception):
    pass


# Filled in once the ML data owner's artifact format is agreed.
LOADERS: dict[str, Callable[[ModelManifest], Recognizer]] = {}


def load_recognizer(model_dir: Path, registry: dict[str, str | None]) -> tuple[Recognizer, ModelManifest]:
    try:
        manifest = load_manifest(model_dir, registry)
    except ManifestError as error:
        raise ModelNotReady(str(error)) from None
    loader = LOADERS.get(manifest.artifact_format)
    if loader is None:
        raise ModelNotReady("unsupported artifact format")
    return loader(manifest), manifest
