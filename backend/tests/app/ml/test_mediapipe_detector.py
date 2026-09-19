import os
from pathlib import Path

import numpy as np
import pytest

from app.config import REPO_ROOT
from app.ml.features import FrameLandmarks
from app.ml.mediapipe_detector import LEFT_WRIST, RIGHT_WRIST, _to_array, assign_hands

MODEL_PATH = Path(
    os.environ.get("POOKIE_HOLISTIC_MODEL", REPO_ROOT / "backend/app/ml/artifacts/mediapipe/holistic_landmarker.task")
)


def pose_with_wrists(left, right):
    pose = np.zeros((33, 2))
    pose[LEFT_WRIST], pose[RIGHT_WRIST] = left, right
    return pose


def hand_at(x, y):
    return np.tile([x, y], (21, 1))


POSE = pose_with_wrists(left=[0.7, 0.5], right=[0.3, 0.5])


def test_two_hands_swapped_back_to_anatomical_sides():
    near_left, near_right = hand_at(0.68, 0.5), hand_at(0.32, 0.5)
    left, right = assign_hands(POSE, near_right, near_left)
    assert left is near_left and right is near_right


def test_two_hands_already_correct_are_kept():
    near_left, near_right = hand_at(0.68, 0.5), hand_at(0.32, 0.5)
    left, right = assign_hands(POSE, near_left, near_right)
    assert left is near_left and right is near_right


@pytest.mark.parametrize("slot", [0, 1])
def test_single_hand_goes_to_nearest_wrist(slot):
    hand = hand_at(0.31, 0.5)
    args = [None, None]
    args[slot] = hand
    left, right = assign_hands(POSE, *args)
    assert left is None and right is hand


def test_without_pose_hands_pass_through():
    a = hand_at(0.1, 0.1)
    assert assign_hands(None, a, None) == (a, None)
    assert assign_hands(POSE, None, None) == (None, None)


def test_to_array_handles_flat_and_nested_lists():
    class P:
        def __init__(self, x, y):
            self.x, self.y = x, y

    flat = [P(0.1, 0.2), P(0.3, 0.4)]
    np.testing.assert_allclose(_to_array(flat), [[0.1, 0.2], [0.3, 0.4]])
    np.testing.assert_allclose(_to_array([flat]), [[0.1, 0.2], [0.3, 0.4]])
    assert _to_array([]) is None and _to_array(None) is None


@pytest.mark.skipif(not MODEL_PATH.is_file(), reason="MediaPipe holistic .task model not downloaded")
def test_real_mediapipe_runs_on_empty_frame():
    pytest.importorskip("mediapipe")
    from app.ml.mediapipe_detector import MediaPipeHolisticDetector

    detector = MediaPipeHolisticDetector(MODEL_PATH)
    try:
        result = detector.detect(np.zeros((480, 640, 3), np.uint8))
    finally:
        detector.close()
    assert isinstance(result, FrameLandmarks)
    assert result.pose is None and result.left_hand is None and result.right_hand is None
