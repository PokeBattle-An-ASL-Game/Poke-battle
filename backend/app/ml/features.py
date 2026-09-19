import hashlib
import json
import math
from dataclasses import dataclass
from typing import Protocol, Sequence

import numpy as np

EXTRACTOR_VERSION = "pookie-landmarks-v0-draft"
FRAME_COUNT = 25
LANDMARK_MODEL_SHA256 = "e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8"

# MediaPipe pose indices: nose, eyes, mouth corners, shoulders, elbows, wrists.
POSE_POINTS = (0, 2, 5, 9, 10, 11, 12, 13, 14, 15, 16)
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
HAND_POINTS = 21
POSE_DIM = len(POSE_POINTS) * 2
HAND_DIM = HAND_POINTS * 2
FEATURE_DIM = POSE_DIM + 2 * HAND_DIM
MASK_CHANNELS = ("pose", "left_hand", "right_hand")

MIN_POSE_FRAMES = 13
MIN_HAND_FRAMES = 5
MIN_SHOULDER_WIDTH_PX = 8.0


class ExtractorInputError(ValueError):
    pass


@dataclass(frozen=True)
class FrameLandmarks:
    """Normalized [0,1] x,y image coordinates of the raw, unmirrored frame.

    Hands are the signer's anatomical left/right.
    """

    pose: np.ndarray | None = None
    left_hand: np.ndarray | None = None
    right_hand: np.ndarray | None = None


class LandmarkDetector(Protocol):
    def detect(self, frame_rgb: np.ndarray) -> FrameLandmarks: ...


@dataclass(frozen=True)
class FeatureSequence:
    features: np.ndarray
    mask: np.ndarray
    timestamps_ms: np.ndarray
    extractor_version: str
    reason: str | None


def extractor_fingerprint() -> str:
    layout = {
        "version": EXTRACTOR_VERSION,
        "landmark_model": LANDMARK_MODEL_SHA256,
        "frames": FRAME_COUNT,
        "pose": POSE_POINTS,
        "hand": HAND_POINTS,
        "mask": MASK_CHANNELS,
        "thresholds": [MIN_POSE_FRAMES, MIN_HAND_FRAMES, MIN_SHOULDER_WIDTH_PX],
    }
    return hashlib.sha256(json.dumps(layout, sort_keys=True).encode()).hexdigest()


def validate_timestamps(timestamps_ms: Sequence[float]) -> np.ndarray:
    if len(timestamps_ms) != FRAME_COUNT:
        raise ExtractorInputError(f"expected {FRAME_COUNT} timestamps")
    values = []
    for value in timestamps_ms:
        if isinstance(value, bool) or not isinstance(value, (int, float, np.number)) or not math.isfinite(value):
            raise ExtractorInputError("timestamps must be finite numbers")
        values.append(float(value))
    stamps = np.asarray(values, dtype=np.float64)
    if np.any(np.diff(stamps) <= 0):
        raise ExtractorInputError("timestamps must be strictly increasing")
    return stamps


def validate_frames(frames_rgb: Sequence[np.ndarray]) -> tuple[int, int]:
    if len(frames_rgb) != FRAME_COUNT:
        raise ExtractorInputError(f"expected {FRAME_COUNT} frames")
    shape = None
    for frame in frames_rgb:
        if not isinstance(frame, np.ndarray) or frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3:
            raise ExtractorInputError("frames must be HxWx3 uint8 RGB arrays")
        if shape is not None and frame.shape != shape:
            raise ExtractorInputError("all frames must share one size")
        shape = frame.shape
    return shape[1], shape[0]


def _points(array: np.ndarray | None, count: int) -> np.ndarray | None:
    if array is None:
        return None
    array = np.asarray(array, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] != count or array.shape[1] < 2:
        raise ExtractorInputError("unexpected landmark array shape")
    xy = array[:, :2]
    return xy if np.all(np.isfinite(xy)) else None


def features_from_landmarks(
    landmarks: Sequence[FrameLandmarks], timestamps_ms: Sequence[float], image_size: tuple[int, int]
) -> FeatureSequence:
    stamps = validate_timestamps(timestamps_ms)
    if len(landmarks) != FRAME_COUNT:
        raise ExtractorInputError(f"expected {FRAME_COUNT} landmark frames")
    width, height = image_size
    pixels = np.array([width, height], dtype=np.float64)

    features = np.zeros((FRAME_COUNT, FEATURE_DIM), dtype=np.float32)
    mask = np.zeros((FRAME_COUNT, len(MASK_CHANNELS)), dtype=bool)

    for i, frame in enumerate(landmarks):
        pose = _points(frame.pose, 33)
        if pose is None:
            continue
        pose = pose * pixels
        origin = (pose[LEFT_SHOULDER] + pose[RIGHT_SHOULDER]) / 2
        scale = float(np.linalg.norm(pose[LEFT_SHOULDER] - pose[RIGHT_SHOULDER]))
        if scale < MIN_SHOULDER_WIDTH_PX:
            continue
        features[i, :POSE_DIM] = ((pose[list(POSE_POINTS)] - origin) / scale).ravel()
        mask[i, 0] = True
        for channel, hand in enumerate((frame.left_hand, frame.right_hand), start=1):
            points = _points(hand, HAND_POINTS)
            if points is None:
                continue
            start = POSE_DIM + (channel - 1) * HAND_DIM
            features[i, start : start + HAND_DIM] = ((points * pixels - origin) / scale).ravel()
            mask[i, channel] = True

    reason = None
    if mask[:, 0].sum() < MIN_POSE_FRAMES:
        reason = "no_person"
    elif (mask[:, 1] | mask[:, 2]).sum() < MIN_HAND_FRAMES:
        reason = "hands_not_visible"
    return FeatureSequence(features, mask, stamps - stamps[0], EXTRACTOR_VERSION, reason)


POSE_MIRROR = {2: 5, 5: 2, 9: 10, 10: 9, 11: 12, 12: 11, 13: 14, 14: 13, 15: 16, 16: 15}


def mirror_sequence(sequence: FeatureSequence) -> FeatureSequence:
    """Left-right mirror of a sequence, e.g. to augment training with left-handed signing."""
    frames = sequence.features.reshape(sequence.features.shape[0], -1, 2)
    pose_count = len(POSE_POINTS)
    pose_order = [POSE_POINTS.index(POSE_MIRROR.get(point, point)) for point in POSE_POINTS]
    left = frames[:, pose_count : pose_count + HAND_POINTS]
    right = frames[:, pose_count + HAND_POINTS :]
    mirrored = np.concatenate([frames[:, pose_order], right, left], axis=1)
    mirrored[..., 0] *= -1
    return FeatureSequence(
        mirrored.reshape(sequence.features.shape).astype(np.float32),
        sequence.mask[:, [0, 2, 1]].copy(),
        sequence.timestamps_ms.copy(),
        sequence.extractor_version,
        sequence.reason,
    )


def extract_features(
    frames_rgb: Sequence[np.ndarray], timestamps_ms: Sequence[float], detector: LandmarkDetector
) -> FeatureSequence:
    image_size = validate_frames(frames_rgb)
    validate_timestamps(timestamps_ms)
    return features_from_landmarks([detector.detect(frame) for frame in frames_rgb], timestamps_ms, image_size)


def sample_frame_indices(frame_count: int, fps: float, start: int = 0, end: int | None = None):
    """Evenly pick FRAME_COUNT frames from a source video span; returns (indices, timestamps_ms)."""
    end = frame_count - 1 if end is None else end
    if fps <= 0 or end - start + 1 < FRAME_COUNT:
        raise ExtractorInputError(f"need at least {FRAME_COUNT} source frames")
    indices = np.floor(np.linspace(start, end, FRAME_COUNT) + 0.5).astype(int)
    return indices.tolist(), ((indices - start) * 1000.0 / fps).tolist()
