import re
import tempfile

import werkzeug.formparser

from app import create_app
from app.config import Config, REPO_ROOT

ORIGIN = "http://localhost:5173"


def test_uploads_never_spill_to_disk(make_client, post_attempt, make_jpeg, monkeypatch):
    def no_disk(*args, **kwargs):
        raise AssertionError("upload written to a temporary file")

    monkeypatch.setattr(werkzeug.formparser, "SpooledTemporaryFile", no_disk)
    monkeypatch.setattr(tempfile, "TemporaryFile", no_disk)
    oversized_frame = b"\xff\xd8\xff" + b"\0" * 600_000
    response = post_attempt(make_client(), frames=[oversized_frame] + [make_jpeg()] * (Config.FRAME_COUNT - 1))
    assert response.status_code == 413
    assert post_attempt(make_client()).status_code == 200


def test_debug_is_off_by_default():
    app = create_app()
    assert app.debug is False and app.testing is False


def test_no_hardcoded_credentials_in_backend_source():
    pattern = re.compile(r"(api[_-]?key|secret|password|token)\s*[=:]\s*['\"][^'\"]+['\"]", re.IGNORECASE)
    sources = [p for p in (REPO_ROOT / "backend").rglob("*.py") if ".venv" not in p.parts]
    assert sources
    assert [str(p) for p in sources if pattern.search(p.read_text(encoding="utf-8"))] == []


def test_only_one_application_route(make_client):
    rules = {(rule.rule, method) for rule in make_client().application.url_map.iter_rules()
             for method in rule.methods - {"HEAD", "OPTIONS"}}
    assert rules == {("/api/validate-sign", "POST")}


def test_other_paths_are_json_errors(make_client):
    client = make_client()
    for response, status in ((client.get("/api/health"), 404), (client.get("/api/validate-sign"), 405)):
        assert response.status_code == status
        assert response.get_json()["requestId"] is None


def test_cors_preflight_allows_configured_origin_only(make_client):
    client = make_client(CORS_ORIGINS=[ORIGIN])
    headers = {"Access-Control-Request-Method": "POST"}
    allowed = client.options("/api/validate-sign", headers={"Origin": ORIGIN, **headers})
    denied = client.options("/api/validate-sign", headers={"Origin": "https://evil.example", **headers})
    assert allowed.headers.get("Access-Control-Allow-Origin") == ORIGIN
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_real_repo_data_without_model_is_not_ready(post_attempt, tmp_path):
    client = create_app({"MODEL_DIR": tmp_path / "no-model"}).test_client()
    assert client.application.extensions["pookie"]["recognizer"] is None
    response = post_attempt(client)
    assert (response.status_code, response.get_json()["error"]["code"]) == (503, "MODEL_NOT_READY")


def test_real_repo_sign_requires_manifest_qualification(post_attempt, fake_recognizer):
    # Real level-1 move-1 is CITY; a manifest that only qualifies SECRETARY must not judge it.
    from pathlib import Path

    from app.ml.manifest import ModelManifest

    manifest = ModelManifest("fake-v1", "fake", ("SECRETARY",), frozenset({"SECRETARY"}), Path("x"))
    recognizer = fake_recognizer()
    client = create_app(recognizer=recognizer, manifest=manifest).test_client()
    response = post_attempt(client)
    assert (response.status_code, response.get_json()["error"]["code"]) == (422, "SIGN_UNAVAILABLE")
    assert recognizer.calls == 0
