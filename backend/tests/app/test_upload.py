import io
import json
import uuid

import pytest
from werkzeug.datastructures import FileStorage, MultiDict

from app import upload as u

REQUEST_ID = str(uuid.uuid4())
STAMPS = [i * 100.0 for i in range(25)]


@pytest.fixture
def config(config):
    # This module's fixtures assume 25 frames regardless of the app's configured FRAME_COUNT.
    return {**config, "FRAME_COUNT": 25}


def form(**overrides):
    fields = {"requestId": REQUEST_ID, "levelId": "1", "moveId": "move-1", "timestampsMs": json.dumps(STAMPS)}
    fields.update(overrides)
    return MultiDict([(k, v) for k, v in fields.items() if v is not None])


def files(frames, mimetype="image/jpeg"):
    return MultiDict([("frames", FileStorage(io.BytesIO(f), "f.jpg", content_type=mimetype)) for f in frames])


def test_valid_attempt(config, make_jpeg):
    attempt = u.parse_attempt(form(), files([make_jpeg()] * 25), config)
    assert attempt.request_id == REQUEST_ID and attempt.level_id == 1 and attempt.move_id == "move-1"
    assert attempt.timestamps_ms == STAMPS and len(attempt.frames_jpeg) == 25


@pytest.mark.parametrize(
    "fields",
    [
        {"requestId": None},
        {"requestId": "not-a-uuid"},
        {"requestId": "{" + REQUEST_ID + "}"},
        {"levelId": "abc"},
        {"levelId": "01"},
        {"moveId": "../level-2"},
        {"moveId": ""},
        {"expectedSign": "CITY"},
        {"timestampsMs": "not json"},
        {"timestampsMs": json.dumps(STAMPS[:24])},
        {"timestampsMs": json.dumps(STAMPS[:24] + [2300.0])},
        {"timestampsMs": json.dumps(STAMPS[:24]).replace("]", ", NaN]")},
        {"timestampsMs": json.dumps([True] * 25)},
        {"timestampsMs": json.dumps([i * 10.0 for i in range(25)])},
        {"timestampsMs": json.dumps([i * 1000.0 for i in range(25)])},
    ],
)
def test_bad_fields_rejected(config, make_jpeg, fields):
    with pytest.raises(u.BadUpload):
        u.parse_attempt(form(**fields), files([make_jpeg()] * 25), config)


def test_duplicate_field_rejected(config, make_jpeg):
    duplicated = form()
    duplicated.add("moveId", "move-2")
    with pytest.raises(u.BadUpload):
        u.parse_attempt(duplicated, files([make_jpeg()] * 25), config)


@pytest.mark.parametrize("count", [0, 24, 26])
def test_wrong_frame_count(config, make_jpeg, count):
    with pytest.raises(u.BadUpload):
        u.parse_attempt(form(), files([make_jpeg()] * count), config)


def test_wrong_mimetype_or_fake_jpeg(config, make_jpeg):
    with pytest.raises(u.BadUpload):
        u.parse_attempt(form(), files([make_jpeg()] * 25, mimetype="image/png"), config)
    with pytest.raises(u.BadUpload):
        u.parse_attempt(form(), files([b"GIF89a..."] * 25), config)


def test_unexpected_file_field(config, make_jpeg):
    extra = files([make_jpeg()] * 25)
    extra.add("other", FileStorage(io.BytesIO(make_jpeg()), "x.jpg", content_type="image/jpeg"))
    with pytest.raises(u.BadUpload):
        u.parse_attempt(form(), extra, config)


def test_oversized_frame(config):
    big = u.JPEG_MAGIC + b"\0" * config["MAX_FRAME_BYTES"]
    with pytest.raises(u.UploadTooLarge):
        u.parse_attempt(form(), files([big] * 25), config)


def test_decode_frames(config, make_jpeg):
    frames = u.decode_frames([make_jpeg()] * 25, config)
    assert len(frames) == 25 and frames[0].shape == (48, 64, 3) and frames[0].dtype.name == "uint8"


def test_decode_rejects_bad_images(config, make_jpeg):
    good = make_jpeg()
    for frames in (
        [good[: len(good) // 2]] * 25,
        [make_jpeg(1281, 720)] * 25,
        [make_jpeg(640, 721)] * 25,
        [good] * 24 + [make_jpeg(32, 32)],
        [u.JPEG_MAGIC + b"garbage"] * 25,
    ):
        with pytest.raises(u.BadUpload):
            u.decode_frames(frames, config)
