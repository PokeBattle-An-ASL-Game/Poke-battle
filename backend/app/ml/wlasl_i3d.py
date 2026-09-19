import math
from typing import Callable, Sequence

import cv2
import numpy as np

from ..config import Config
from .manifest import ModelManifest
from .recognizer import ModelNotReady, Prediction

FORMAT = "wlasl-i3d"
PREPROCESSING_VERSION = "wlasl-i3d-bgr-fit256-crop224-max64-v1"
SHORT_SIDE = 256
CROP = 224
MAX_FRAMES = 64
MIN_PROB = 0.25
MIN_MARGIN = 3.0


def sample_indices(count: int, target: int = MAX_FRAMES) -> list[int]:
    if count <= target:
        return list(range(count))
    return np.floor(np.linspace(0, count - 1, target) + 0.5).astype(int).tolist()


def _to_model_frame(frame_rgb: np.ndarray) -> np.ndarray:
    bgr = np.ascontiguousarray(frame_rgb[..., ::-1])
    scale = SHORT_SIDE / min(bgr.shape[:2])
    resized = cv2.resize(bgr, dsize=(0, 0), fx=scale, fy=scale)
    return (resized.astype(np.float32) / 255.0) * 2.0 - 1.0


def preprocess(frames_rgb: Sequence[np.ndarray]) -> np.ndarray:
    frames = [_to_model_frame(frames_rgb[i]) for i in sample_indices(len(frames_rgb))]
    video = np.asarray(frames, dtype=np.float64)
    height, width = video.shape[1:3]
    top = int(np.round((height - CROP) / 2.0))
    left = int(np.round((width - CROP) / 2.0))
    video = video[:, top : top + CROP, left : left + CROP, :]
    return video.transpose(3, 0, 1, 2).astype(np.float32)[np.newaxis]


def _softmax(scores: np.ndarray) -> np.ndarray:
    exp = np.exp(scores - scores.max())
    return exp / exp.sum()


def decide(scores: np.ndarray, class_to_sign: dict[int, str], model_version: str,
           min_prob: float = MIN_PROB, min_margin: float = MIN_MARGIN) -> Prediction:
    order = np.argsort(scores)[::-1]
    top1, top2 = int(order[0]), int(order[1])
    margin = float(scores[top1] - scores[top2])
    max_prob = float(_softmax(scores)[top1])
    label = class_to_sign.get(top1)
    if max_prob < min_prob or margin < min_margin or label is None:
        return Prediction(None, max_prob, "uncertain_prediction", model_version)
    return Prediction(label, max_prob, None, model_version)


class WlaslRecognizer:
    def __init__(self, model: Callable[[np.ndarray], np.ndarray], class_to_sign: dict[int, str],
                 model_version: str, min_prob: float = MIN_PROB, min_margin: float = MIN_MARGIN):
        self.model = model
        self.class_to_sign = dict(class_to_sign)
        self.model_version = model_version
        self.min_prob = min_prob
        self.min_margin = min_margin

    def predict_sequence(self, frames_rgb: Sequence[np.ndarray], timestamps_ms: Sequence[float]) -> Prediction:
        logits = np.asarray(self.model(preprocess(frames_rgb)), dtype=np.float64)
        scores = logits[0].max(axis=1)
        return decide(scores, self.class_to_sign, self.model_version, self.min_prob, self.min_margin)


def _number(value, low: float, high: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and low <= value <= high


def read_settings(manifest: ModelManifest) -> tuple[dict[int, str], int, float, float]:
    data = manifest.settings
    if data.get("preprocessingVersion") != PREPROCESSING_VERSION:
        raise ModelNotReady("wlasl preprocessing version mismatch")
    frame_count = data.get("frameCount")
    if isinstance(frame_count, bool) or frame_count != Config.FRAME_COUNT:
        raise ModelNotReady("wlasl frame count mismatch")
    num_classes = data.get("numClasses")
    if not isinstance(num_classes, int) or isinstance(num_classes, bool) or num_classes < 2:
        raise ModelNotReady("wlasl numClasses invalid")
    class_map = data.get("classMap")
    if not isinstance(class_map, dict) or not all(
        isinstance(key, str) and key.isascii() and key.isdigit() and int(key) < num_classes for key in class_map
    ):
        raise ModelNotReady("wlasl classMap keys must be class indices")
    class_to_sign = {int(key): sign for key, sign in class_map.items()}
    signs = list(class_to_sign.values())
    if len(class_to_sign) != len(class_map) or len(set(signs)) != len(signs) or set(signs) != set(manifest.labels):
        raise ModelNotReady("wlasl classMap must map one class to each label")
    min_prob, min_margin = data.get("minProb"), data.get("minMargin")
    if not _number(min_prob, 0.0, 1.0) or not _number(min_margin, 0.0, math.inf):
        raise ModelNotReady("wlasl thresholds invalid")
    return class_to_sign, num_classes, float(min_prob), float(min_margin)


def build_model(weights_path, num_classes: int) -> Callable[[np.ndarray], np.ndarray]:
    from .wlasl_torch import load_i3d

    return load_i3d(weights_path, num_classes)


def load_wlasl_recognizer(manifest: ModelManifest) -> WlaslRecognizer:
    class_to_sign, num_classes, min_prob, min_margin = read_settings(manifest)
    model = build_model(manifest.weights_path, num_classes)
    return WlaslRecognizer(model, class_to_sign, manifest.model_version, min_prob, min_margin)
