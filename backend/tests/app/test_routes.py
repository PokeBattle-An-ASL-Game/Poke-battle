import pytest

from app.ml.recognizer import Prediction


def error_code(response):
    return response.get_json()["error"]["code"]


def test_correct_response_matches_contract(make_client, post_attempt):
    response = post_attempt(make_client(), requestId="583fe810-53c8-42ab-9c70-64f7264c8255")
    assert response.status_code == 200
    assert response.get_json() == {
        "requestId": "583fe810-53c8-42ab-9c70-64f7264c8255", "status": "correct", "correct": True,
        "expectedSign": "HELLO", "recognizedSign": "HELLO", "confidence": 0.9, "reason": None,
        "modelVersion": "fake-v1",
    }


@pytest.mark.parametrize(
    "prediction, status, reason",
    [
        (Prediction("YES", 0.8, None, "fake-v1"), "incorrect", "different_sign"),
        (Prediction(None, None, "hands_not_visible", "fake-v1"), "retry", "hands_not_visible"),
        (Prediction(None, 0.3, "something_else", "fake-v1"), "retry", "uncertain_prediction"),
        (Prediction("NO", 0.99, None, "fake-v1"), "retry", "uncertain_prediction"),
        (Prediction("HELLO", 0.9, "uncertain_prediction", "fake-v1"), "retry", "uncertain_prediction"),
    ],
)
def test_incorrect_and_retry(make_client, post_attempt, fake_recognizer, prediction, status, reason):
    body = post_attempt(make_client(fake_recognizer(prediction))).get_json()
    assert (body["status"], body["reason"]) == (status, reason)
    if status == "retry":
        assert body["correct"] is None and body["recognizedSign"] is None and body["confidence"] is None


@pytest.mark.parametrize(
    "fields, frames, status, code",
    [
        ({"levelId": "abc"}, None, 400, "BAD_REQUEST"),
        ({"expectedSign": "HELLO"}, None, 400, "BAD_REQUEST"),
        ({"levelId": "9"}, None, 404, "NOT_FOUND"),
        ({"moveId": "move-7"}, None, 404, "NOT_FOUND"),
        ({"levelId": "2"}, None, 422, "LEVEL_UNAVAILABLE"),
        ({"levelId": "3", "moveId": "move-1"}, None, 422, "SIGN_UNAVAILABLE"),
        ({}, [b"\xff\xd8\xff broken"] * 25, 400, "BAD_REQUEST"),
    ],
)
def test_errors(make_client, post_attempt, fake_recognizer, fields, frames, status, code):
    recognizer = fake_recognizer()
    response = post_attempt(make_client(recognizer), frames=frames, **fields)
    assert (response.status_code, error_code(response)) == (status, code)
    assert recognizer.calls == 0


def test_request_id_echoed_on_error_and_null_when_invalid(make_client, post_attempt):
    client = make_client()
    rid = "583fe810-53c8-42ab-9c70-64f7264c8255"
    assert post_attempt(client, requestId=rid, levelId="9").get_json()["requestId"] == rid
    assert post_attempt(client, requestId="nope").get_json()["requestId"] is None


@pytest.mark.parametrize(
    "prediction, error",
    [
        (None, RuntimeError("boom")),
        (Prediction("HELLO", 0.9, None, "other-model"), None),
        (Prediction("HELLO", float("nan"), None, "fake-v1"), None),
        (Prediction("HELLO", 1.5, None, "fake-v1"), None),
        ("not a prediction", None),
    ],
)
def test_broken_inference_is_503_not_incorrect(make_client, post_attempt, fake_recognizer, prediction, error):
    response = post_attempt(make_client(fake_recognizer(prediction, error)))
    assert (response.status_code, error_code(response)) == (503, "INFERENCE_UNAVAILABLE")


def test_no_model_is_503_never_correct(make_client, post_attempt):
    response = post_attempt(make_client(manifest=None))
    assert (response.status_code, error_code(response)) == (503, "MODEL_NOT_READY")


def test_oversized_request_is_413(make_client, post_attempt):
    response = post_attempt(make_client(MAX_CONTENT_LENGTH=10_000))
    assert (response.status_code, error_code(response)) == (413, "UPLOAD_TOO_LARGE")


def test_non_multipart_rejected(make_client):
    response = make_client().post("/api/validate-sign", json={"levelId": 1})
    assert (response.status_code, error_code(response)) == (400, "BAD_REQUEST")
