from typing import Callable, Sequence

import cv2
import numpy as np

from .recognizer import Prediction

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
