import numpy as np
import pytest

from app.ml import features as f

STAMPS = [i * 100.0 for i in range(25)]
SIZE = (640, 480)


def pose(shift_x=0.0):
    points = np.full((33, 2), 0.5)
    points[f.LEFT_SHOULDER] = [0.6, 0.6]
    points[f.RIGHT_SHOULDER] = [0.4, 0.6]
    return points + [shift_x, 0.0]


def hand(x, y):
    return np.tile([x, y], (21, 1))


def frames_with(**kwargs):
    return [f.FrameLandmarks(**kwargs) for _ in range(25)]


def test_shape_mask_and_version():
    seq = f.features_from_landmarks(frames_with(pose=pose(), left_hand=hand(0.7, 0.4)), STAMPS, SIZE)
    assert seq.features.shape == (25, f.FEATURE_DIM) and seq.features.dtype == np.float32
    assert seq.mask.shape == (25, 3)
    assert seq.mask[:, 0].all() and seq.mask[:, 1].all() and not seq.mask[:, 2].any()
    assert seq.extractor_version == f.EXTRACTOR_VERSION
    assert seq.reason is None
    assert seq.timestamps_ms[0] == 0 and seq.timestamps_ms[-1] == 2400


def test_body_relative_units():
    seq = f.features_from_landmarks(frames_with(pose=pose(), left_hand=hand(0.7, 0.6)), STAMPS, SIZE)
    assert seq.features[0, f.POSE_DIM] == pytest.approx(1.0)
    assert seq.features[0, f.POSE_DIM + 1] == pytest.approx(0.0)


def test_translation_invariant_but_location_preserved():
    a = f.features_from_landmarks(frames_with(pose=pose(), right_hand=hand(0.5, 0.3)), STAMPS, SIZE)
    b = f.features_from_landmarks(frames_with(pose=pose(0.1), right_hand=hand(0.6, 0.3)), STAMPS, SIZE)
    c = f.features_from_landmarks(frames_with(pose=pose(), right_hand=hand(0.5, 0.55)), STAMPS, SIZE)
    np.testing.assert_allclose(a.features, b.features, atol=1e-6)
    assert not np.allclose(a.features, c.features)


def test_missing_hands_are_zero_and_masked():
    seq = f.features_from_landmarks(frames_with(pose=pose()), STAMPS, SIZE)
    assert not seq.features[:, f.POSE_DIM :].any()
    assert not seq.mask[:, 1:].any()
    assert seq.reason == "hands_not_visible"


def test_no_person():
    seq = f.features_from_landmarks(frames_with(left_hand=hand(0.5, 0.5)), STAMPS, SIZE)
    assert seq.reason == "no_person"
    assert not seq.mask.any() and not seq.features.any()


def test_nan_landmarks_are_masked_not_propagated():
    bad = hand(0.5, 0.5)
    bad[3, 0] = np.nan
    seq = f.features_from_landmarks(frames_with(pose=pose(), left_hand=bad), STAMPS, SIZE)
    assert np.isfinite(seq.features).all()
    assert not seq.mask[:, 1].any()


@pytest.mark.parametrize(
    "stamps",
    [STAMPS[:24], STAMPS + [2500.0], [0.0] * 25, STAMPS[:24] + [float("nan")], list(reversed(STAMPS)), [True] * 25],
)
def test_bad_timestamps_rejected(stamps):
    with pytest.raises(f.ExtractorInputError):
        f.validate_timestamps(stamps)


def test_frame_validation():
    good = [np.zeros((48, 64, 3), np.uint8)] * 25
    assert f.validate_frames(good) == (64, 48)
    bad_inputs = (
        good[:24],
        [np.zeros((48, 64), np.uint8)] * 25,
        [np.zeros((48, 64, 3), np.float32)] * 25,
        good[:24] + [np.zeros((10, 10, 3), np.uint8)],
    )
    for bad in bad_inputs:
        with pytest.raises(f.ExtractorInputError):
            f.validate_frames(bad)


def test_extract_features_uses_detector_per_frame():
    class Detector:
        calls = 0

        def detect(self, frame):
            Detector.calls += 1
            return f.FrameLandmarks(pose=pose(), right_hand=hand(0.5, 0.5))

    seq = f.extract_features([np.zeros((48, 64, 3), np.uint8)] * 25, STAMPS, Detector())
    assert Detector.calls == 25 and seq.mask[:, 2].all()


def test_sample_frame_indices():
    indices, stamps = f.sample_frame_indices(frame_count=75, fps=30)
    assert len(indices) == 25 and indices[0] == 0 and indices[-1] == 74
    assert all(b > a for a, b in zip(indices, indices[1:]))
    f.validate_timestamps(stamps)
    exact, _ = f.sample_frame_indices(frame_count=25, fps=25)
    assert exact == list(range(25))
    with pytest.raises(f.ExtractorInputError):
        f.sample_frame_indices(frame_count=24, fps=30)


def asymmetric_person():
    rng = np.random.default_rng(0)
    body = pose() + rng.normal(0, 0.01, (33, 2))
    return f.FrameLandmarks(pose=body, left_hand=hand(0.72, 0.35) + rng.normal(0, 0.01, (21, 2)), right_hand=None)


def mirror_image(frame):
    flip = np.array([-1.0, 1.0])
    body = frame.pose * flip + [1.0, 0.0]
    for a, b in f.POSE_MIRROR.items():
        if a < b:
            body[[a, b]] = body[[b, a]]
    flipped = [None if h is None else h * flip + [1.0, 0.0] for h in (frame.left_hand, frame.right_hand)]
    return f.FrameLandmarks(pose=body, left_hand=flipped[1], right_hand=flipped[0])


def test_mirror_matches_a_physically_mirrored_person():
    person = [asymmetric_person()] * 25
    original = f.features_from_landmarks(person, STAMPS, (480, 480))
    mirrored_person = f.features_from_landmarks([mirror_image(p) for p in person], STAMPS, (480, 480))
    mirrored = f.mirror_sequence(original)
    np.testing.assert_allclose(mirrored.features, mirrored_person.features, atol=1e-5)
    np.testing.assert_array_equal(mirrored.mask, mirrored_person.mask)


def test_mirror_twice_is_identity_and_keeps_metadata():
    original = f.features_from_landmarks([asymmetric_person()] * 25, STAMPS, SIZE)
    twice = f.mirror_sequence(f.mirror_sequence(original))
    np.testing.assert_allclose(twice.features, original.features)
    np.testing.assert_array_equal(twice.mask, original.mask)
    once = f.mirror_sequence(original)
    assert once.mask[:, 2].all() and not once.mask[:, 1].any()
    assert once.features.dtype == np.float32 and once.extractor_version == original.extractor_version


def test_fingerprint_is_stable():
    assert f.extractor_fingerprint() == f.extractor_fingerprint()
    assert len(f.extractor_fingerprint()) == 64
