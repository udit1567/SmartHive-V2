# SmartHive V2

An IoT hive dashboard: eight unlabeled datastreams (**D1–D8**), live webcam or camera-URL detection, and plant-health checks.

This folder is the current product. The original Flask + React app stays in `../SmartHive` as a reference and is not overwritten.

---

## What’s in the box

| Area | What you get |
| --- | --- |
| **Dashboard** | Blynk-style widgets bound to D1–D8 (value, gauge, chart). Live board vs edit board. |
| **Plant health** | Soil-moisture trend plus leaf-disease detection (still image or live stream). |
| **Object detection** | YOLO on an upload, laptop webcam, or HTTP snapshot / MJPEG URL. |
| **Devices** | Per-user `auth_token`. Boards `POST /update` with that token in `Authorization`. |
| **Account** | Signup, login (JWT), profile. |

Auth and sensors run without PyTorch. Vision routes return **503** until the `.pt` weights are on disk.

---

## Stack

```
frontend/          Vue 3 + Vite + Vue Router + Pinia   →  http://localhost:5173
backend/           Flask + SQLAlchemy + JWT            →  http://127.0.0.1:5000
```

- UI is hand-styled (oasis palette). No component library.
- Routing is **hash-based** (`/#/app`, `/#/app/plants`) so static hosting does not need rewrite rules.
- Default API port is **5000** (the old `run.py` used 5001 while the client already called 5000).

---

## Layout

```
SmartHive-V2/
├── backend/
│   ├── app/                 # factory, models, auth, sensors, vision
│   ├── run.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── yolov8l.pt           # object model (gitignored) — copy locally
│   └── best.pt              # plant model (gitignored) — copy locally
└── frontend/
    ├── src/
    │   ├── views/           # home, auth, dashboard, plants, sight, device, account
    │   ├── components/      # widgets, live stream, detect panel, moisture graph
    │   └── stores/          # session, sensors, dashboard layout
    └── package.json
```

---

## Prerequisites

- **Python 3.11** — YOLO / torch wheels are unreliable on 3.14
- **Node.js 18+**
- Optional: `yolov8l.pt` and `best.pt` in `backend/` (copy from the original SmartHive backend)

---

## Quick start

### 1. API

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then replace the placeholder secrets
python run.py                      # http://127.0.0.1:5000
```

### 2. Weights (vision only)

Place files next to `run.py`, or set absolute paths in `.env`:

| File | Role | Env |
| --- | --- | --- |
| `yolov8l.pt` | Objects | `YOLO_OBJECT_WEIGHTS` |
| `best.pt` | Plant disease | `YOLO_PLANT_WEIGHTS` |

`*.pt` files are gitignored. Detection images are stored under `DETECTION_FOLDER` (default `Detection images/`).

### 3. Web app

```bash
cd frontend
cp .env.example .env               # VITE_API_URL=http://127.0.0.1:5000
npm install
npm run dev                        # http://localhost:5173
```

Production build: `npm run build` then `npm run preview`.

---

## Using the app

1. Sign up, then log in.
2. **Add Device** — copy the device token.
3. **Edit** — drag widgets onto the board and bind each to D1–D8.
4. **Dashboard** — live readings only (no palette).
5. **Plant Health** / **Object Detection** — upload a still, or start **laptop webcam** / paste a camera URL.

Widget layout is saved in `localStorage` as `smarthive.widgets.<uid>`.

---

## Device ingest

Firmware (or curl) posts pin values with the **raw** device token — not `Bearer`.

```http
POST /update
Authorization: YOUR_AUTH_TOKEN
Content-Type: application/json

{ "D1": 24.5, "D2": 61, "D3": 40 }
```

Pins are unlabeled on purpose. Name them on the dashboard (for example D1 = temperature, D3 = soil moisture).

---

## API

Base URL: `http://127.0.0.1:5000`

### Auth

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/signup` | JSON: `username`, `email`, `firstName`, `lastName`, `password`, `address`, `source` |
| `POST` | `/login` | Returns `access_token`, `auth_token`, `email`, `uid` |
| `POST` | `/logout` | `Authorization: Bearer <access_token>` |
| `GET` | `/profile/<email>` | Bearer JWT; email must match the token |

### Sensors

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/update` | Device token in `Authorization` |
| `GET` | `/get_data/<id>` | History for user id |
| `GET` | `/get_d1/<id>` … `/get_d8/<id>` | Latest non-null reading per pin |

### Vision

Device token in `Authorization` (same raw token as `/update`).

| Method | Path | Body |
| --- | --- | --- |
| `POST` | `/detect_objects` | multipart `image` |
| `POST` | `/detect_plant_disease` | multipart `image` |
| `POST` | `/detect_objects_base64` | JSON `image_base64` |
| `POST` | `/detect_plant_disease_base64` | JSON `image_base64` |
| `POST` | `/detect_live_objects` | multipart `image`, or JSON `{ "source_url": "http://…" }` |
| `POST` | `/detect_live_plant_disease` | same as live objects |
| `GET` | `/fetch_object_detection_images` | Saved stills |
| `GET` | `/fetch_plant_disease_images` | Saved stills |
| `GET` | `/get-image/<category>/<api_token>/<filename>` | `object-detection` or `plant-disease` |

Live endpoints do **not** write every frame to disk. Camera URLs must be `http://` or `https://` (snapshot JPEG or MJPEG).

---

## Environment

### `backend/.env`

| Variable | Default |
| --- | --- |
| `SECRET_KEY` | — set a real secret |
| `JWT_SECRET_KEY` | — set a real secret |
| `DATABASE_URI` | `sqlite:///build.sqlite3` |
| `YOLO_OBJECT_WEIGHTS` | `yolov8l.pt` (resolved from the backend folder) |
| `YOLO_PLANT_WEIGHTS` | `best.pt` |
| `DETECTION_FOLDER` | `Detection images` |
| `HOST` | `0.0.0.0` |
| `PORT` | `5000` |

### `frontend/.env`

| Variable | Default |
| --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:5000` |

---

## License

Use and extend as you like for this project. YOLO weights remain under their own licenses (Ultralytics / your trained `best.pt`).
