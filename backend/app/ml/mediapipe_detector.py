from pathlib import Path

import numpy as np

from .features import FrameLandmarks

LEFT_WRIST, RIGHT_WRIST = 15, 16


def _to_array(landmarks) -> np.ndarray | None:
    if not landmarks:
        return None
    if isinstance(landmarks[0], list):
        landmarks = landmarks[0]
    return np.array([[p.x, p.y] for p in landmarks], dtype=np.float64)


def assign_hands(pose, hand_a, hand_b):
    hands = [h for h in (hand_a, hand_b) if h is not None]
    if pose is None or not hands:
        return hand_a, hand_b
    left, right = pose[LEFT_WRIST], pose[RIGHT_WRIST]
    if len(hands) == 1:
        hand = hands[0]
        closer_left = np.linalg.norm(hand[0] - left) <= np.linalg.norm(hand[0] - right)
        return (hand, None) if closer_left else (None, hand)
    a, b = hands
    straight = np.linalg.norm(a[0] - left) + np.linalg.norm(b[0] - right)
    swapped = np.linalg.norm(b[0] - left) + np.linalg.norm(a[0] - right)
    return (a, b) if straight <= swapped else (b, a)


class MediaPipeHolisticDetector:
    def __init__(self, model_path: str | Path):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision

        self._mp = mp
        options = vision.HolisticLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.IMAGE,
        )
        self._landmarker = vision.HolisticLandmarker.create_from_options(options)

    def detect(self, frame_rgb: np.ndarray) -> FrameLandmarks:
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=np.ascontiguousarray(frame_rgb))
        result = self._landmarker.detect(image)
        pose = _to_array(result.pose_landmarks)
        left, right = assign_hands(pose, _to_array(result.left_hand_landmarks), _to_array(result.right_hand_landmarks))
        return FrameLandmarks(pose=pose, left_hand=left, right_hand=right)

    def close(self) -> None:
        self._landmarker.close()
