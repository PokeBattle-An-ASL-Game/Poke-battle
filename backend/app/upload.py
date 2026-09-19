import io
import json
import math
import re
import uuid
from dataclasses import dataclass

import numpy as np
from PIL import Image, UnidentifiedImageError

FORM_FIELDS = {"requestId", "levelId", "moveId", "timestampsMs"}
LEVEL_ID_PATTERN = re.compile(r"[1-9][0-9]{0,2}")
MOVE_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,32}")
JPEG_MAGIC = b"\xff\xd8\xff"


class BadUpload(Exception):
    pass


class UploadTooLarge(Exception):
    pass


@dataclass(frozen=True)
class Attempt:
    request_id: str
    level_id: int
    move_id: str
    timestamps_ms: list[float]
    frames_jpeg: list[bytes]


def read_request_id(form) -> str | None:
    values = form.getlist("requestId")
    if len(values) != 1:
        return None
    try:
        return values[0] if str(uuid.UUID(values[0])) == values[0].lower() else None
    except ValueError:
        return None


def _reject_constant(name):
    raise ValueError(name)


def parse_timestamps(raw: str, config) -> list[float]:
    try:
        values = json.loads(raw, parse_constant=_reject_constant)
    except ValueError:
        raise BadUpload("timestampsMs must be a JSON array") from None
    if not isinstance(values, list) or len(values) != config["FRAME_COUNT"]:
        raise BadUpload("timestampsMs must have one entry per frame")
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0 for v in values):
        raise BadUpload("timestampsMs must be finite non-negative numbers")
    if any(b <= a for a, b in zip(values, values[1:])):
        raise BadUpload("timestampsMs must be strictly increasing")
    if not config["MIN_SEQUENCE_SPAN_MS"] <= values[-1] - values[0] <= config["MAX_SEQUENCE_SPAN_MS"]:
        raise BadUpload("capture duration out of range")
    return [float(v) for v in values]


def read_frames(files, config) -> list[bytes]:
    if len(files) != config["FRAME_COUNT"]:
        raise BadUpload("wrong number of frames")
    frames = []
    for storage in files:
        if storage.mimetype != "image/jpeg":
            raise BadUpload("frames must be image/jpeg")
        data = storage.stream.read(config["MAX_FRAME_BYTES"] + 1)
        if len(data) > config["MAX_FRAME_BYTES"]:
            raise UploadTooLarge("frame too large")
        if not data.startswith(JPEG_MAGIC):
            raise BadUpload("frame is not a JPEG")
        frames.append(data)
    return frames


def parse_attempt(form, files, config) -> Attempt:
    if set(form.keys()) != FORM_FIELDS or set(files.keys()) != {"frames"}:
        raise BadUpload("missing or unexpected fields")
    if any(len(form.getlist(key)) != 1 for key in FORM_FIELDS):
        raise BadUpload("duplicate field")
    request_id = read_request_id(form)
    if request_id is None:
        raise BadUpload("requestId must be a UUID")
    if not LEVEL_ID_PATTERN.fullmatch(form["levelId"]) or not MOVE_ID_PATTERN.fullmatch(form["moveId"]):
        raise BadUpload("invalid levelId or moveId")
    timestamps = parse_timestamps(form["timestampsMs"], config)
    frames = read_frames(files.getlist("frames"), config)
    return Attempt(request_id, int(form["levelId"]), form["moveId"], timestamps, frames)


def decode_frames(frames_jpeg: list[bytes], config) -> list[np.ndarray]:
    decoded, size = [], None
    for data in frames_jpeg:
        try:
            with Image.open(io.BytesIO(data), formats=["JPEG"]) as image:
                width, height = image.size
                if width > config["MAX_FRAME_WIDTH"] or height > config["MAX_FRAME_HEIGHT"]:
                    raise BadUpload("frame dimensions too large")
                if size is not None and image.size != size:
                    raise BadUpload("frames must share one size")
                size = image.size
                decoded.append(np.asarray(image.convert("RGB"), dtype=np.uint8))
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
            raise BadUpload("invalid JPEG frame") from None
    return decoded
