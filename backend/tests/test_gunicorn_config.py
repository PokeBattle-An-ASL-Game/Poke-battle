import importlib


def test_production_defaults_are_private(monkeypatch):
    monkeypatch.delenv("POOKIE_BIND", raising=False)
    monkeypatch.delenv("POOKIE_WORKERS", raising=False)
    config = importlib.reload(importlib.import_module("gunicorn_config"))
    assert config.accesslog is None
    assert config.bind.startswith("127.0.0.1:")
    assert config.workers >= 1 and config.timeout <= 60
