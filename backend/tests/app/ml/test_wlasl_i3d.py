from pathlib import Path

import cv2
import numpy as np
import pytest

from app.ml import wlasl_i3d as w
from app.ml.manifest import ModelManifest
from app.ml.recognizer import ModelNotReady

CLASSES = {3: "HELLO", 7: "YES"}


def trial_preprocess(frames_bgr):
    imgs = []
    for img in frames_bgr:
        sc = 256.0 / min(img.shape[:2])
        img = cv2.resize(img, dsize=(0, 0), fx=sc, fy=sc)
        imgs.append((img.astype(np.float32) / 255.0) * 2.0 - 1.0)
    arr = np.asarray(imgs, dtype=np.float64)
    _, h, w_, _ = arr.shape
    i, j = int(np.round((h - 224) / 2.0)), int(np.round((w_ - 224) / 2.0))
    arr = arr[:, i:i + 224, j:j + 224, :]
    return arr.transpose(3, 0, 1, 2).astype(np.float32)[np.newaxis]


def random_frames(count, height, width, seed=0):
    rng = np.random.default_rng(seed)
    return [rng.integers(0, 256, (height, width, 3), dtype=np.uint8) for _ in range(count)]


def logits(values, size=100):
    scores = np.zeros(size)
    for index, value in values.items():
        scores[index] = value
    return scores


@pytest.mark.parametrize("height,width", [(480, 640), (720, 1280), (640, 480), (48, 64)])
def test_preprocess_matches_trial_pipeline(height, width):
    frames = random_frames(3, height, width)
    expected = trial_preprocess([f[..., ::-1] for f in frames])
    np.testing.assert_array_equal(w.preprocess(frames), expected)


def test_preprocess_shape_and_range():
    video = w.preprocess(random_frames(25, 480, 640))
    assert video.shape == (1, 3, 25, 224, 224) and video.dtype == np.float32
    assert video.min() >= -1.0 and video.max() <= 1.0


def test_preprocess_swaps_rgb_to_bgr():
    red = np.zeros((240, 320, 3), np.uint8)
    red[..., 0] = 255
    video = w.preprocess([red])
    assert np.all(video[0, 0] == -1.0) and np.all(video[0, 2] == 1.0)


def test_sample_indices_keeps_short_clips_and_spreads_long_ones():
    assert w.sample_indices(25) == list(range(25))
    long = w.sample_indices(100)
    assert len(long) == 64 and long[0] == 0 and long[-1] == 99
    assert long == np.floor(np.linspace(0, 99, 64) + 0.5).astype(int).tolist()


def test_decide_accepts_confident_known_sign():
    prediction = w.decide(logits({3: 10.0, 7: 2.0}), CLASSES, "v1")
    assert prediction.label == "HELLO" and prediction.reason is None
    assert 0.25 <= prediction.score <= 1.0 and prediction.model_version == "v1"


def test_decide_rejects_small_logit_margin():
    prediction = w.decide(logits({3: 10.0, 7: 7.5}), CLASSES, "v1")
    assert prediction.label is None and prediction.reason == "uncertain_prediction"


def test_decide_rejects_low_probability_over_all_classes():
    prediction = w.decide(logits({3: 3.2}), CLASSES, "v1")
    assert prediction.score < 0.25 and prediction.reason == "uncertain_prediction"


def test_decide_rejects_confident_class_outside_label_map():
    prediction = w.decide(logits({50: 12.0, 3: 1.0}), CLASSES, "v1")
    assert prediction.label is None and prediction.reason == "uncertain_prediction"


def test_decide_keeps_other_classes_in_margin():
    prediction = w.decide(logits({3: 10.0, 50: 9.0}), CLASSES, "v1")
    assert prediction.label is None


def test_decide_uses_custom_thresholds():
    prediction = w.decide(logits({3: 10.0, 7: 7.5}), CLASSES, "v1", min_margin=2.0)
    assert prediction.label == "HELLO"


def test_recognizer_takes_max_logit_over_time():
    seen = []

    def fake_model(video):
        seen.append(video.shape)
        out = np.zeros((1, 100, 4))
        out[0, 7, 2] = 12.0
        return out

    recognizer = w.WlaslRecognizer(fake_model, CLASSES, "v1")
    prediction = recognizer.predict_sequence(random_frames(25, 480, 640), [i * 100.0 for i in range(25)])
    assert seen == [(1, 3, 25, 224, 224)]
    assert prediction.label == "YES" and prediction.reason is None


def wlasl_manifest(**overrides):
    settings = {"preprocessingVersion": w.PREPROCESSING_VERSION, "frameCount": 25, "numClasses": 100,
                "classMap": {"3": "HELLO", "7": "YES"}, "minProb": 0.3, "minMargin": 2.5, **overrides}
    return ModelManifest("v1", "wlasl-i3d", ("HELLO", "YES"), frozenset({"HELLO"}), Path("w.pt"), settings)


def test_loader_builds_recognizer_from_manifest(monkeypatch):
    calls = []
    monkeypatch.setattr(w, "build_model", lambda path, n: calls.append((path, n)) or "model")
    recognizer = w.load_wlasl_recognizer(wlasl_manifest())
    assert calls == [(Path("w.pt"), 100)]
    assert recognizer.model == "model" and recognizer.class_to_sign == CLASSES
    assert (recognizer.model_version, recognizer.min_prob, recognizer.min_margin) == ("v1", 0.3, 2.5)


@pytest.mark.parametrize(
    "overrides",
    [
        {"preprocessingVersion": "other"},
        {"frameCount": 64},
        {"frameCount": True},
        {"numClasses": 1},
        {"numClasses": "100"},
        {"classMap": {"3": "HELLO", "x": "YES"}},
        {"classMap": {"3": "HELLO", "100": "YES"}},
        {"classMap": {"3": "HELLO", "-7": "YES"}},
        {"classMap": {"3": "HELLO", "03": "YES"}},
        {"classMap": {"3": "HELLO", "7": "HELLO"}},
        {"classMap": {"3": "HELLO"}},
        {"classMap": {"3": "HELLO", "7": "WATER"}},
        {"classMap": ["HELLO", "YES"]},
        {"minProb": 1.5},
        {"minProb": "0.25"},
        {"minProb": None},
        {"minMargin": -1},
        {"minMargin": True},
        {"minMargin": float("nan")},
    ],
)
def test_invalid_wlasl_settings_not_ready(overrides):
    with pytest.raises(ModelNotReady):
        w.read_settings(wlasl_manifest(**overrides))
