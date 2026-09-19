import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .features import EXTRACTOR_VERSION, FRAME_COUNT, extractor_fingerprint

MANIFEST_FILE = "manifest.json"


class ManifestError(Exception):
    pass


@dataclass(frozen=True)
class ModelManifest:
    model_version: str
    artifact_format: str
    labels: tuple[str, ...]
    qualified_labels: frozenset[str]
    weights_path: Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(data: dict, key: str, kind: type):
    value = data.get(key)
    if not isinstance(value, kind) or isinstance(value, bool):
        raise ManifestError(f"manifest field {key!r} missing or invalid")
    return value


def load_manifest(model_dir: Path, registry: dict[str, str | None]) -> ModelManifest:
    path = Path(model_dir) / MANIFEST_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ManifestError("no model manifest") from None
    except (OSError, ValueError):
        raise ManifestError("model manifest unreadable") from None
    if not isinstance(data, dict) or data.get("manifestVersion") != 1:
        raise ManifestError("unsupported manifest version")

    if _require(data, "extractorVersion", str) != EXTRACTOR_VERSION:
        raise ManifestError("extractor version mismatch")
    if _require(data, "extractorFingerprint", str) != extractor_fingerprint():
        raise ManifestError("extractor fingerprint mismatch")
    if _require(data, "frameCount", int) != FRAME_COUNT:
        raise ManifestError("frame count mismatch")

    labels = _require(data, "labels", list)
    qualified = _require(data, "qualifiedLabels", list)
    if not all(isinstance(label, str) for label in labels + qualified):
        raise ManifestError("labels must be strings")
    if len(set(labels)) != len(labels) or not set(labels) <= set(registry):
        raise ManifestError("labels must be unique registry sign IDs")
    if not set(qualified) <= set(labels):
        raise ManifestError("qualified labels must be model labels")

    weights_file = _require(data, "weightsFile", str)
    if Path(weights_file).name != weights_file or weights_file.startswith("."):
        raise ManifestError("weights file must be a plain file name")
    weights_path = Path(model_dir) / weights_file
    if not weights_path.is_file() or _sha256(weights_path) != _require(data, "weightsSha256", str):
        raise ManifestError("weights missing or checksum mismatch")

    return ModelManifest(
        model_version=_require(data, "modelVersion", str),
        artifact_format=_require(data, "artifactFormat", str),
        labels=tuple(labels),
        qualified_labels=frozenset(qualified),
        weights_path=weights_path,
    )


def is_sign_qualified(sign_id: str, registry: dict[str, str | None], manifest: ModelManifest) -> bool:
    return registry.get(sign_id) is not None and sign_id in manifest.qualified_labels
