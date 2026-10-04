# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SmartHive V2 is an IoT hive dashboard: eight unlabeled sensor pins (D1–D8), live webcam/camera-URL object detection, and plant-health (leaf disease) detection. It is a rewrite of an older Flask + React app that still lives in `../SmartHive` as a reference — do not touch that folder.

- `frontend/` — Vue 3 + Vite + Vue Router + Pinia, served at `http://localhost:5173`
- `backend/` — Flask + SQLAlchemy + JWT, served at `http://127.0.0.1:5000`

## Commands

### Backend (from `backend/`)

```bash
python3.11 -m venv .venv && source .venv/bin/activate   # Python 3.11 required — torch/YOLO wheels are unreliable on newer versions
pip install -r requirements.txt
cp .env.example .env        # set real SECRET_KEY / JWT_SECRET_KEY
python run.py                # http://127.0.0.1:5000, debug=True
```

There is no lint or test tooling configured in the backend.

### Frontend (from `frontend/`)

```bash
npm install
npm run dev       # http://localhost:5173
npm run build
npm run preview
```

There is no lint or test tooling configured in the frontend.

### Weights (vision endpoints only)

Auth and sensor routes work without them. Vision routes (`/detect_*`) return `503` until `yolov8l.pt` (objects) and `best.pt` (plant disease) are placed in `backend/`, or `YOLO_OBJECT_WEIGHTS` / `YOLO_PLANT_WEIGHTS` point at absolute paths. Both are gitignored.

## Architecture

### Two distinct auth mechanisms — do not mix them up

1. **JWT bearer** (`flask_jwt_extended`) — for human/browser endpoints: `/login`, `/signup`, `/logout`, `/profile/<email>`. Frontend sends `Authorization: Bearer <access_token>`.
2. **Raw device token** (`User.auth_token`, generated at signup, looked up via `get_device_user()` in `backend/app/auth.py`) — for machine endpoints: `/update` and every `/detect_*` and `/fetch_*_images` route. Callers send the token **unprefixed** in `Authorization` (no `Bearer`). The frontend's `api/client.js` distinguishes these via the `token` (Bearer) vs `deviceToken` (raw) request options.

The JWT access token auto-refreshes: `auth.py`'s `refresh_expiring_jwts` after-request hook reissues a token (embedded in the JSON body as `access_token`) whenever the current one is within 30 minutes of expiring — the frontend must read that field back out of responses, not just at login.

### Backend structure (`backend/app/`)

- `__init__.py` — application factory (`create_app`); registers `db`/`jwt`/`cors` extensions and the three blueprints, then `db.create_all()`.
- `config.py` — env-driven `Config`; `_path()` resolves relative weight/detection-folder paths against the backend root so they work regardless of CWD.
- `models.py` — `User` and `Data`. `Data` has exactly 8 nullable float columns `D1`..`D8` (no per-user schema — pins are intentionally unlabeled; the frontend assigns meaning to each pin).
- `routes/auth.py`, `routes/sensors.py`, `routes/vision.py` — one blueprint per concern.
- `routes/vision.py` — the least trivial module:
  - YOLO models are lazy-loaded on first use and cached in a module-level `_models` dict keyed by `"object"`/`"plant"`, so the first detection request pays the load cost. `torch`/`ultralytics` are imported lazily too, so the whole app still runs (auth + sensors) when those packages aren't installed.
  - File/base64 detection endpoints save an annotated copy of every processed frame under `DETECTION_FOLDER/<object-detection|plant-disease>/<device_token>/<n>.jpg` (sequential numbering via `_next_image_path`); served back via `/get-image/<category>/<api_token>/<filename>`.
  - Live endpoints (`/detect_live_objects`, `/detect_live_plant_disease`) intentionally do **not** persist frames to disk, and accept three input shapes: multipart `image`, JSON `image_base64`, or JSON `source_url` (an HTTP snapshot or MJPEG stream, fetched and cropped to a single JPEG by `_read_remote_frame`/`_crop_jpeg`). Only `http://`/`https://` source URLs are accepted.

### Frontend structure (`frontend/src/`)

- Routing (`router/index.js`) is **hash-based** (`createWebHashHistory`) specifically so a static host needs no server-side rewrite rules. Routes under `/app` carry `meta: { requiresAuth: true }` and are guarded in `router.beforeEach` against `useAuthStore().isAuthenticated`.
- `stores/auth.js` — session (`access_token`, `auth_token`, `email`, `uid`) persisted to `localStorage["smarthive.session"]`; other stores read `useAuthStore()` directly rather than receiving it as a prop.
- `stores/dashboard.js` — widget layout (type/pin/color/min/max bindings for value/gauge/chart widgets) persisted per-user to `localStorage["smarthive.widgets.<uid>"]`, keyed off `auth.uid`. This is client-only state; the backend has no concept of widgets.
- `stores/sensors.js` — polls `/get_data/<uid>` plus one `/get_d<n>/<uid>` request per pin every 15s (`startPolling`) to populate both full history (`series`) and latest-per-pin (`latestByKey`).
- `constants/pins.js` — the canonical list of pin IDs (`D1`..`D8`) and the widget type/color palettes; add new widget types or colors here, not inline in components.
- `api/client.js` — single fetch wrapper (`request()`) shared by all stores; throws `ApiError` (with `.status`/`.payload`) on non-2xx. Pass `token` for Bearer auth or `deviceToken` for raw device-token auth — never set `Authorization` manually elsewhere.

### Device/firmware contract

Boards POST sensor readings with the raw device token, not a JWT:

```http
POST /update
Authorization: <auth_token>
Content-Type: application/json

{ "D1": 24.5, "D2": 61, "D3": 40 }
```

Pins are deliberately unlabeled at the API/DB level — semantic meaning (e.g. D1 = temperature) is assigned only in the frontend dashboard config, per user.
