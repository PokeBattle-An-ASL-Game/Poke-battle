import logging
import math

from flask import Blueprint, current_app, jsonify, request

from .game_data import LevelNotFound, LevelUnavailable, MoveNotFound, load_level, resolve_sign
from .ml.manifest import is_sign_qualified
from .ml.recognizer import Prediction
from .upload import BadUpload, UploadTooLarge, decode_frames, parse_attempt, read_request_id

api = Blueprint("api", __name__)
log = logging.getLogger(__name__)

RETRY_REASONS = {"no_person", "hands_not_visible", "incomplete_sequence", "uncertain_prediction"}
ERRORS = {
    "BAD_REQUEST": (400, "The sign attempt could not be read."),
    "NOT_FOUND": (404, "Unknown level or move."),
    "UPLOAD_TOO_LARGE": (413, "The upload is too large."),
    "LEVEL_UNAVAILABLE": (422, "This level is not available yet."),
    "SIGN_UNAVAILABLE": (422, "This sign is not available yet."),
    "MODEL_NOT_READY": (503, "Recognition is temporarily unavailable."),
    "INFERENCE_UNAVAILABLE": (503, "Recognition is temporarily unavailable."),
    "INTERNAL_ERROR": (500, "Something went wrong."),
}


class ApiError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def error_response(request_id, code):
    status, message = ERRORS[code]
    return jsonify({"requestId": request_id, "error": {"code": code, "message": message}}), status


@api.post("/api/validate-sign")
def validate_sign():
    if request.mimetype != "multipart/form-data":
        return error_response(None, "BAD_REQUEST")
    request_id = read_request_id(request.form)
    try:
        return jsonify(_validate(request_id))
    except ApiError as error:
        log.info("validate-sign rejected: %s", error.code)
        return error_response(request_id, error.code)


def _validate(request_id):
    config = current_app.config
    state = current_app.extensions["pookie"]
    try:
        attempt = parse_attempt(request.form, request.files, config)
    except BadUpload:
        raise ApiError("BAD_REQUEST") from None
    except UploadTooLarge:
        raise ApiError("UPLOAD_TOO_LARGE") from None

    try:
        level = load_level(config["LEVELS_DIR"], attempt.level_id, config["LEVEL_IDS"])
        sign_id = resolve_sign(level, attempt.move_id)
    except (LevelNotFound, MoveNotFound):
        raise ApiError("NOT_FOUND") from None
    except LevelUnavailable as error:
        log.warning("level %s misconfigured: %s", attempt.level_id, error)
        raise ApiError("LEVEL_UNAVAILABLE") from None
    if not level.available:
        raise ApiError("LEVEL_UNAVAILABLE")

    recognizer, manifest = state["recognizer"], state["manifest"]
    if recognizer is None or manifest is None:
        raise ApiError("MODEL_NOT_READY")
    if not is_sign_qualified(sign_id, state["registry"], manifest):
        raise ApiError("SIGN_UNAVAILABLE")

    try:
        frames = decode_frames(attempt.frames_jpeg, config)
    except BadUpload:
        raise ApiError("BAD_REQUEST") from None
    try:
        prediction = recognizer.predict_sequence(frames, attempt.timestamps_ms)
    except Exception as error:
        log.error("inference failed: %s", type(error).__name__)
        raise ApiError("INFERENCE_UNAVAILABLE") from None
    finally:
        del frames
    if not _is_valid_prediction(prediction, manifest):
        raise ApiError("INFERENCE_UNAVAILABLE")
    return _result(request_id, sign_id, prediction, manifest)


def _is_valid_prediction(prediction, manifest) -> bool:
    if not isinstance(prediction, Prediction) or prediction.model_version != manifest.model_version:
        return False
    if prediction.label is not None and not isinstance(prediction.label, str):
        return False
    score = prediction.score
    return score is None or (
        isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(score) and 0 <= score <= 1
    )


def _result(request_id, sign_id, prediction, manifest) -> dict:
    accepted = (
        prediction.label is not None and prediction.reason is None and prediction.label in manifest.qualified_labels
    )
    if accepted and prediction.label == sign_id:
        status, correct, reason = "correct", True, None
    elif accepted:
        status, correct, reason = "incorrect", False, "different_sign"
    else:
        status, correct = "retry", None
        reason = prediction.reason if prediction.reason in RETRY_REASONS else "uncertain_prediction"
    return {
        "requestId": request_id,
        "status": status,
        "correct": correct,
        "expectedSign": sign_id,
        "recognizedSign": prediction.label if accepted else None,
        "confidence": prediction.score if accepted else None,
        "reason": reason,
        "modelVersion": prediction.model_version,
    }
