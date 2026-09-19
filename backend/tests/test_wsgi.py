def test_wsgi_exposes_the_single_route_app():
    from wsgi import app

    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert routes == {"/api/validate-sign"}
    assert app.debug is False
