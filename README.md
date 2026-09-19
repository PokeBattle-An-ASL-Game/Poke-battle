# PookieBattle

A Pokémon-style battle game where players attack by performing American Sign Language (ASL) words in front of their webcam.

> **Status: in development.** The React UI and the Flask `POST /api/validate-sign` backend exist, but there is **no working ASL recognition yet**: the UI's camera step is still simulated, and no model manifest is installed. All seven levels are `available: true` (team decision), but the server only judges a sign once it is validated (see below).

## Planned architecture

| Part | Tech | Responsibility |
| --- | --- | --- |
| `frontend/` | React + TypeScript | UI, camera capture, battle state (HP, PP, four attack slots, FIFO reserve queue), opponent turns, versioned `localStorage` progress |
| `backend/` | Flask + Python ML | A single application endpoint, `POST /api/validate-sign`, that checks a captured sign against the expected move |
| `shared/` | JSON | Sign registry and draft narration lines shared by frontend and backend |

The backend never stores HP, PP, moves, progress, camera images or landmarks. There are no user accounts, database or server-side game sessions.

## Game data

- `frontend/src/constants/levels.json` — index of the seven level cards.
- `frontend/src/constants/levels/level-1.json` … `level-7.json` — each level's own moves, damage and opponent. **30 unique proposed ASL words** split 2/3/4/4/5/6/6 across the levels.
  - Every move has `maxPP: 1`; move damage in each level sums to the opponent's 100 HP.
  - Opponent attacks deal 10 HP.
- `shared/signs.json` — the 30 proposed sign IDs. Model labels, reference videos and teaching notes are `null` until reviewed.
- `shared/voice-lines.json` — draft narration text (no audio generated yet).

## Assets

`frontend/public/assets/` holds placeholders only. Opponent art (`pokemon/*.png`), narration audio and ASL video clips are **git-ignored** until distribution rights are confirmed. See the README in each asset folder.

## Setup

Prerequisites: Node.js 18+ (frontend) and Python 3.12 (backend).

```bash
git clone https://github.com/RohithNair27/Poke-battle.git
cd Poke-battle
```

(The repository will be renamed to `pookie-battle`; update the URL above once that rename happens on GitHub.)

To check that the level JSON files parse:

```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('frontend/src/constants/**/*.json', recursive=True) + glob.glob('shared/*.json')]; print('OK')"
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev      # serves http://localhost:5173
npm run build    # production build into frontend/dist
```

The battle screen's sign-capture step records real webcam frames (`frontend/src/constants/capture.js`'s `FRAME_COUNT`, 64 by default — must match the backend's `POOKIE_FRAME_COUNT`) and posts them to `POST /api/validate-sign` at `VITE_API_BASE_URL` (defaults to `http://localhost:5000`).

### Backend (Flask API + shared feature extractor)

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-ml.txt -r requirements-dev.txt
.venv/bin/python -m app.ml.holistic_model   # downloads the pinned MediaPipe model and checks its SHA-256
.venv/bin/python -m pytest                  # run the backend tests
.venv/bin/flask --app "app:create_app()" run   # serves http://localhost:5000
```

For production use gunicorn instead of the Flask dev server (no access log, so client IPs are never logged; uploads stay in memory):

```bash
POOKIE_BIND=127.0.0.1:8000 POOKIE_CORS_ORIGINS=https://your-frontend.example .venv/bin/gunicorn -c gunicorn_config.py wsgi:app
```

#### WLASL I3D model (non-commercial only)

The backend can run the pretrained WLASL100 I3D video model. **The WLASL dataset and its pretrained weights are released under the C-UDA licence for academic, non-commercial use only.** Never commit or publicly share the weights. Download WLASL's pretrained weights archive yourself from https://drive.google.com/uc?id=1jALimVOB69ifYkeT0Pe297S1z4U3jC48 and unzip it; the checkpoint is `archived/asl100/FINAL_nslt_100_iters=896_top1=65.89_top5=84.11_top10=89.92.pt` (SHA-256 `a61d7dda5f875ce5ebd9d407c56874f77d1cd2aeb4bc7cd0d98a6e1ca4669a0c`).

```bash
.venv/bin/python -m app.ml.wlasl_torch /path/to/FINAL_nslt_100_iters=896_top1=65.89_top5=84.11_top10=89.92.pt
```

This downloads WLASL's `pytorch_i3d.py` (pinned commit, SHA-256 checked) into `app/ml/artifacts/wlasl/` and copies the checkpoint to `app/ml/artifacts/wlasl100_i3d.pt` after checking its SHA-256. The server still answers `503 MODEL_NOT_READY` until a `manifest.json` with the agreed class map and webcam-tested thresholds is added.

With the server running, `tools/sample_request.sh [base_url] [levelId] [moveId]` sends one real request built with `Config.FRAME_COUNT` frames (64 by default). Until a qualified model exists and a level is enabled, expect `422 LEVEL_UNAVAILABLE` or `503 MODEL_NOT_READY`; that is the intended honest behaviour.

Environment variables (all optional):

| Variable | Default |
| --- | --- |
| `POOKIE_CORS_ORIGINS` | `http://localhost:5173` (comma-separated) |
| `POOKIE_MODEL_DIR` | `backend/app/ml/artifacts` |
| `POOKIE_LEVELS_DIR` | `frontend/src/constants/levels` |
| `POOKIE_FRAME_COUNT` | `64` (frames per `POST /api/validate-sign` attempt; must match the frontend capture count and the WLASL manifest's `frameCount`) |
| `POOKIE_SIGNS_PATH` | `shared/signs.json` |

Every possible API response is listed in `shared/api-examples/responses.json`; a backend test keeps it identical to what the server actually returns, so frontend mocks can use it directly.

## Contributing rules

- Don't commit `.env` files, API keys, datasets, videos, extracted features or model weights (see `.gitignore`).
- Levels are `available: true` by team decision. The server only judges a sign that has a `modelLabel` in `shared/signs.json` and is in the model's `qualifiedLabels`; otherwise it answers `422 SIGN_UNAVAILABLE`. Don't add either until the sign has reviewed teaching material, confirmed usage rights and measured model support.
- Don't present mock or simulated recognition as a working ASL model.
