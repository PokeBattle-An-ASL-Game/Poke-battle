# PokeBattle

A Pokémon-style battle game where players attack by performing American Sign Language (ASL) words in front of their webcam.

> **Status: Code Complete.** The React UI and the Flask `POST /api/validate-sign` backend exist. A provisional WLASL100 I3D manifest template is committed, but recognition is **not webcam-validated** yet and the UI's camera step is still simulated. Only level 1 unlocks by default — the rest open as the player clears their way up, tracked in `localStorage` — and the server only judges a sign once it is validated (see below).

## Architecture

| Part | Tech | Responsibility |
| --- | --- | --- |
| `frontend/` | React + TypeScript | UI, camera capture, battle state (HP, PP, four attack slots, FIFO reserve queue), opponent turns, versioned `localStorage` progress |
| `backend/` | Flask + Python ML | A single application endpoint, `POST /api/validate-sign`, that checks a captured sign against the expected move |
| `shared/` | JSON | Sign registry and draft narration lines shared by frontend and backend |

The backend never stores HP, PP, moves, progress, camera images or landmarks. There are no user accounts, database or server-side game sessions.

## Game data

- `frontend/src/constants/levels.json` — index of the seven level cards; its `available` flags are only design defaults, seeded into `localStorage` on first load with just level 1 unlocked.
- `frontend/src/constants/levels/level-1.json` … `level-7.json` — each level's own moves, damage and opponent. **18 unique WLASL signs** are reused across **29 move slots**, split 2/2/4/4/5/6/6 across the levels.
  - A sign may repeat across different levels, but never twice within the same level.
  - Every move has `maxPP: 1`; move damage in each level sums to the opponent's 100 HP.
  - Opponent attacks deal 10 HP.
- `shared/signs.json` — **19** sign IDs with non-null `modelLabel` values matching lowercase WLASL100 glosses (the 18 level signs plus **BUT**). The vocabulary and acceptance thresholds are **provisional** and have not yet been fully webcam-validated.
- `shared/voice-lines.json` — draft narration text (no audio generated yet).

## Assets

`frontend/public/assets/` holds placeholders only. Opponent art (`pokemon/*.png`), narration audio and ASL video clips are **git-ignored** until distribution rights are confirmed. See the README in each asset folder.

## Setup

Prerequisites: Node.js 18+ (frontend) and Python 3.12 (backend).

```bash
git clone https://github.com/RohithNair27/Poke-battle.git
cd Poke-battle
```

(The repository will be renamed to `Poke-battle`; update the URL above once that rename happens on GitHub.)

To check that the level JSON files parse:

```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('frontend/src/constants/**/*.json', recursive=True) + glob.glob('shared/*.json')]; print('OK')"
```

### Frontend (React + Vite)

Uses Node 22.13.0 (pinned in `frontend/.nvmrc` and `frontend/.tool-versions`; `nvm use` or asdf picks it up).

```bash
cd frontend
npm install
npm run dev      # serves http://localhost:5173
npm run build    # production build into frontend/dist
```

The battle screen's sign-capture step records real webcam frames (`frontend/src/constants/capture.js`'s `FRAME_COUNT`, 64 by default — must match the backend's `Poke_FRAME_COUNT`) and posts them to `POST /api/validate-sign` at `VITE_API_BASE_URL` (defaults to `http://localhost:5001`).

### Backend (Flask API + shared feature extractor)

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-ml.txt -r requirements-dev.txt
.venv/bin/python -m app.ml.holistic_model   # downloads the pinned MediaPipe model and checks its SHA-256
.venv/bin/python -m pytest                  # run the backend tests
.venv/bin/flask --app "app:create_app()" run --port 5001   # serves http://localhost:5001
```

For production use gunicorn instead of the Flask dev server (no access log, so client IPs are never logged; uploads stay in memory):

```bash
Poke_BIND=127.0.0.1:8000 Poke_CORS_ORIGINS=https://your-frontend.example .venv/bin/gunicorn -c gunicorn_config.py wsgi:app
```

#### WLASL I3D model (non-commercial only)

The backend can run the pretrained WLASL100 I3D video model. **The WLASL dataset and its pretrained weights are released under the C-UDA licence for academic, non-commercial use only.** Never commit or publicly share the weights. Download WLASL's pretrained weights archive yourself from https://drive.google.com/uc?id=1jALimVOB69ifYkeT0Pe297S1z4U3jC48 and unzip it; the checkpoint is `archived/asl100/FINAL_nslt_100_iters=896_top1=65.89_top5=84.11_top10=89.92.pt` (SHA-256 `a61d7dda5f875ce5ebd9d407c56874f77d1cd2aeb4bc7cd0d98a6e1ca4669a0c`).

```bash
.venv/bin/python -m app.ml.wlasl_torch /path/to/FINAL_nslt_100_iters=896_top1=65.89_top5=84.11_top10=89.92.pt
```

This downloads WLASL's `pytorch_i3d.py` (pinned commit, SHA-256 checked) into `app/ml/artifacts/wlasl/`, copies the checkpoint to `app/ml/artifacts/wlasl100_i3d.pt` after checking its SHA-256, and writes `app/ml/artifacts/manifest.json` from the committed template `backend/app/ml/wlasl100_manifest.json` (19 provisional WLASL signs, `minProb` 0.25, `minMargin` 3.0). Vocabulary and thresholds remain provisional until webcam validation is complete; do not treat install as a production-ready recognizer.

With the server running, `tools/sample_request.sh [base_url] [levelId] [moveId]` sends one real request built with `Config.FRAME_COUNT` frames (64 by default). Until a qualified model exists and a level is enabled, expect `422 LEVEL_UNAVAILABLE` or `503 MODEL_NOT_READY`; that is the intended honest behaviour.

Environment variables (all optional):

| Variable | Default |
| --- | --- |
| `Poke_CORS_ORIGINS` | `http://localhost:5173,http://localhost:5174` (comma-separated) |
| `Poke_MODEL_DIR` | `backend/app/ml/artifacts` |
| `Poke_LEVELS_DIR` | `frontend/src/constants/levels` |
| `Poke_FRAME_COUNT` | `64` (frames per `POST /api/validate-sign` attempt; must match the frontend capture count and the WLASL manifest's `frameCount`) |
| `Poke_SIGNS_PATH` | `shared/signs.json` |

Every possible API response is listed in `shared/api-examples/responses.json`; a backend test keeps it identical to what the server actually returns, so frontend mocks can use it directly.

## Contributing rules

- Don't commit `.env` files, API keys, datasets, videos, extracted features or model weights (see `.gitignore`).
- Only level 1 is unlocked by default; later levels unlock as the player clears their way up, tracked in `localStorage` (`Poke.levels`), seeded from `levels.json` on first load. The game uses **18 unique WLASL signs** across **29 move slots** (signs may repeat across levels, not within one level). The registry/manifest also include **BUT** (19 signs total). The server only judges a sign that has a `modelLabel` in `shared/signs.json` and is in the model's `qualifiedLabels`; otherwise it answers `422 SIGN_UNAVAILABLE`. Vocabulary and thresholds remain provisional until webcam validation is complete. Don't add a sign to `qualifiedLabels` until it has reviewed teaching material, confirmed usage rights and measured model support.
- Don't present mock or simulated recognition as a working ASL model.
