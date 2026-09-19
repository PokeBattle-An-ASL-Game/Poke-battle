import json

import pytest

from app import game_data as g
from app.config import Config

LEVEL_IDS = range(1, 8)


def write_level(tmp_path, level_id=1, moves=None, available=True, **extra):
    moves = moves if moves is not None else [{"id": "move-1", "signId": "CITY"}, {"id": "move-2", "signId": "TABLE"}]
    data = {"id": level_id, "available": available, "moves": moves, **extra}
    (tmp_path / f"level-{level_id}.json").write_text(json.dumps(data))


def moves(count):
    return [{"id": f"move-{i}", "signId": f"SIGN_{i}"} for i in range(1, count + 1)]


def test_loads_level_and_resolves_sign(tmp_path):
    write_level(tmp_path)
    level = g.load_level(tmp_path, 1, LEVEL_IDS)
    assert level.available is True
    assert g.resolve_sign(level, "move-2") == "TABLE"
    with pytest.raises(g.MoveNotFound):
        g.resolve_sign(level, "move-3")


@pytest.mark.parametrize("count", [2, 6])
def test_two_to_six_moves_allowed(tmp_path, count):
    write_level(tmp_path, moves=moves(count))
    assert len(g.load_level(tmp_path, 1, LEVEL_IDS).moves) == count


@pytest.mark.parametrize("count", [0, 1, 7])
def test_wrong_move_count_rejected(tmp_path, count):
    write_level(tmp_path, moves=moves(count))
    with pytest.raises(g.LevelUnavailable):
        g.load_level(tmp_path, 1, LEVEL_IDS)


@pytest.mark.parametrize(
    "bad_moves",
    [
        [{"id": "move-1", "signId": "A"}, {"id": "move-1", "signId": "B"}],
        [{"id": "move-1", "signId": "A"}, {"id": "move-2", "signId": "A"}],
        [{"id": "move-1", "signId": "A"}, {"id": 2, "signId": "B"}],
        [{"id": "move-1", "signId": "A"}, "move-2"],
    ],
)
def test_duplicate_or_malformed_moves_rejected(tmp_path, bad_moves):
    write_level(tmp_path, moves=bad_moves)
    with pytest.raises(g.LevelUnavailable):
        g.load_level(tmp_path, 1, LEVEL_IDS)


def test_unknown_or_out_of_range_level_not_found(tmp_path):
    for level_id in (0, 8, 99):
        with pytest.raises(g.LevelNotFound):
            g.load_level(tmp_path, level_id, LEVEL_IDS)
    with pytest.raises(g.LevelNotFound):
        g.load_level(tmp_path, 3, LEVEL_IDS)


def test_mismatched_id_or_broken_json_unavailable(tmp_path):
    write_level(tmp_path, level_id=2)
    (tmp_path / "level-1.json").write_text((tmp_path / "level-2.json").read_text())
    with pytest.raises(g.LevelUnavailable):
        g.load_level(tmp_path, 1, LEVEL_IDS)
    (tmp_path / "level-1.json").write_text("{not json")
    with pytest.raises(g.LevelUnavailable):
        g.load_level(tmp_path, 1, LEVEL_IDS)
    (tmp_path / "level-1.json").write_text("[]")
    with pytest.raises(g.LevelUnavailable):
        g.load_level(tmp_path, 1, LEVEL_IDS)


def test_available_must_be_literally_true(tmp_path):
    write_level(tmp_path, available="true")
    assert g.load_level(tmp_path, 1, LEVEL_IDS).available is False


def test_real_repo_levels_have_30_slots_and_18_unique_signs():
    signs = []
    for level_id in LEVEL_IDS:
        level = g.load_level(Config.LEVELS_DIR, level_id, LEVEL_IDS)
        level_signs = list(level.moves.values())
        assert len(level_signs) == len(set(level_signs))
        assert level.available is True
        signs.extend(level_signs)
    assert len(signs) == 30
    assert len(set(signs)) == 18
    registry = g.load_sign_registry(Config.SIGNS_PATH)
    assert set(signs) <= set(registry)


def test_real_sign_registry():
    registry = g.load_sign_registry(Config.SIGNS_PATH)
    assert len(registry) == 18
    assert "HELLO" not in registry and "CITY" in registry
    assert all(isinstance(label, str) and label for label in registry.values())


def test_bad_registry_rejected(tmp_path):
    path = tmp_path / "signs.json"
    for content in ("{bad", json.dumps({"schemaVersion": 2, "signs": []}),
                    json.dumps({"schemaVersion": 1, "signs": [{"id": "A", "modelLabel": None}] * 2})):
        path.write_text(content)
        with pytest.raises(g.RegistryError):
            g.load_sign_registry(path)
