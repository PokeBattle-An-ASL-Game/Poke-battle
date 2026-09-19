# PokeBattle

A Pokémon-style battle game where players attack by performing American Sign Language (ASL) words in front of their webcam.

> **Status: early scaffold.** This repository currently contains the hardcoded game data (levels, moves, sign IDs) and asset placeholders only. There is **no playable app, Flask backend, or trained ASL model yet**, and all seven levels are `available: false` until each sign is validated.

## Planned architecture

| Part | Tech | Responsibility |
| --- | --- | --- |
| `frontend/` | React + TypeScript | UI, camera capture, battle state (HP, PP, four attack slots, FIFO reserve queue), opponent turns, versioned `localStorage` progress |
| `backend/` *(not yet created)* | Flask + Python ML | A single application endpoint, `POST /api/validate-sign`, that checks a captured sign against the expected move |
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

Prerequisites (for the upcoming app code): Node.js 18+ and Python 3.10+.

```bash
git clone https://github.com/RohithNair27/Poke-battle.git
cd Poke-battle
```

To check that the level JSON files parse:

```bash
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('frontend/src/constants/**/*.json', recursive=True) + glob.glob('shared/*.json')]; print('OK')"
```

Frontend (`npm install`, `npm run dev`) and backend (`python -m venv .venv`, `pip install -r requirements.txt`) setup steps will be added once that code is in place.

## Contributing rules

- Don't commit `.env` files, API keys, datasets, videos, extracted features or model weights (see `.gitignore`).
- Don't set a level to `available: true` until every sign in it has reviewed teaching material, confirmed usage rights and measured model support.
- Don't present mock or simulated recognition as a working ASL model.
