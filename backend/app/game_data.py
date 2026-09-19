import json
from dataclasses import dataclass
from pathlib import Path

MIN_MOVES, MAX_MOVES = 2, 6


class LevelNotFound(Exception):
    pass


class LevelUnavailable(Exception):
    pass


class MoveNotFound(Exception):
    pass


class RegistryError(Exception):
    pass


@dataclass(frozen=True)
class Level:
    id: int
    available: bool
    moves: dict[str, str]


def load_level(levels_dir: Path, level_id: int, allowed_ids) -> Level:
    if level_id not in allowed_ids:
        raise LevelNotFound(level_id)
    path = Path(levels_dir) / f"level-{level_id}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise LevelNotFound(level_id) from None
    except (OSError, ValueError):
        raise LevelUnavailable("level file unreadable") from None

    if not isinstance(data, dict) or data.get("id") != level_id or not isinstance(data.get("moves"), list):
        raise LevelUnavailable("level file malformed")
    moves = data["moves"]
    if not MIN_MOVES <= len(moves) <= MAX_MOVES:
        raise LevelUnavailable("level must have 2-6 moves")
    mapping = {}
    for move in moves:
        move_id = move.get("id") if isinstance(move, dict) else None
        sign_id = move.get("signId") if isinstance(move, dict) else None
        if not isinstance(move_id, str) or not isinstance(sign_id, str) or move_id in mapping:
            raise LevelUnavailable("invalid or duplicate move")
        mapping[move_id] = sign_id
    if len(set(mapping.values())) != len(mapping):
        raise LevelUnavailable("duplicate sign in level")
    return Level(level_id, data.get("available") is True, mapping)


def resolve_sign(level: Level, move_id: str) -> str:
    try:
        return level.moves[move_id]
    except KeyError:
        raise MoveNotFound(move_id) from None


def load_sign_registry(path: Path) -> dict[str, str | None]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        signs = data["signs"]
        registry = {sign["id"]: sign["modelLabel"] for sign in signs}
    except (OSError, ValueError, KeyError, TypeError):
        raise RegistryError("sign registry unreadable") from None
    if data.get("schemaVersion") != 1 or len(registry) != len(signs):
        raise RegistryError("unsupported or duplicate sign registry")
    return registry
