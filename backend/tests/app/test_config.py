from app.config import Config, _origins


def test_default_paths_point_at_shared_repo_files():
    assert (Config.LEVELS_DIR / "level-1.json").is_file()
    assert Config.SIGNS_PATH.is_file()


def test_origins_parsing():
    assert _origins(" https://a.example , ,http://localhost:5173 ") == ["https://a.example", "http://localhost:5173"]
    assert _origins("") == []


def test_limits_match_api_contract():
    assert Config.FRAME_COUNT == 25
    assert Config.MAX_FRAME_BYTES == 200 * 1024
    assert (Config.MAX_FRAME_WIDTH, Config.MAX_FRAME_HEIGHT) == (1280, 720)
    assert Config.MAX_CONTENT_LENGTH == 6 * 1024 * 1024
    assert list(Config.LEVEL_IDS) == list(range(1, 8))
