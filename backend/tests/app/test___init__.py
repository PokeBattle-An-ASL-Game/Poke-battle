from app import create_app

ORIGIN = "http://localhost:5173"


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


def test_real_repo_data_starts_honestly_unavailable(post_attempt):
    client = create_app().test_client()
    assert client.application.extensions["pookie"]["recognizer"] is None
    response = post_attempt(client)
    assert (response.status_code, response.get_json()["error"]["code"]) == (422, "LEVEL_UNAVAILABLE")
