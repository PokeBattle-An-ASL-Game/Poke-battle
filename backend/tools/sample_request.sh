#!/usr/bin/env bash
# Usage: backend/tools/sample_request.sh [base_url] [levelId] [moveId]
set -euo pipefail

BASE_URL="${1:-http://localhost:5001}"
LEVEL_ID="${2:-1}"
MOVE_ID="${3:-move-1}"
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRAMES_DIR="$(mktemp -d)"
trap 'rm -rf "$FRAMES_DIR"' EXIT

read -r REQUEST_ID TIMESTAMPS < <("$BACKEND_DIR/.venv/bin/python" - "$BACKEND_DIR" "$FRAMES_DIR" <<'EOF'
import json, sys, uuid
sys.path.insert(0, sys.argv[1])
from app.config import Config
from PIL import Image
n = Config.FRAME_COUNT
step = min(100, 4900 // max(n - 1, 1))  # stay under MAX_SEQUENCE_SPAN_MS regardless of frame count
for i in range(n):
    Image.new("RGB", (640, 480), (i * 10 % 256, 90, 120)).save(f"{sys.argv[2]}/frame-{i:03d}.jpg", quality=80)
print(uuid.uuid4(), json.dumps([i * step for i in range(n)], separators=(",", ":")))
EOF
)

FRAME_ARGS=()
for frame in "$FRAMES_DIR"/frame-*.jpg; do
  FRAME_ARGS+=(-F "frames=@$frame;type=image/jpeg")
done

curl -sS -w '\nHTTP %{http_code}\n' \
  -F "requestId=$REQUEST_ID" -F "levelId=$LEVEL_ID" -F "moveId=$MOVE_ID" -F "timestampsMs=$TIMESTAMPS" \
  "${FRAME_ARGS[@]}" "$BASE_URL/api/validate-sign"
