# SmartHive-V2

Refactored backend of the original SmartHive app. Frontend is still in the old `SmartHive` folder.

The old `run.py` listened on port **5001** while the React app called **5000**. This backend defaults to **5000**.

## Backend

```bash
cd backend
python3.11 -m venv .venv   # 3.11 matches the old app; YOLO/torch wheels are unreliable on 3.14
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Auth and sensor routes work without torch. Put `yolov8l.pt` and `best.pt` in `backend/` (or set `YOLO_OBJECT_WEIGHTS` / `YOLO_PLANT_WEIGHTS`). Detection routes return 503 until those files exist.

Copy `.env.example` to `.env` and replace the placeholder secrets before any real use.

## Endpoints (same as v1)

- `POST /login`, `POST /signup`, `POST /logout`, `GET /profile/<email>`
- `POST /update` (device `Authorization` header = `auth_token`)
- `GET /get_data/<id>`, `GET /get_d1/<id>` … `/get_d8/<id>`
- `POST /detect_objects`, `/detect_plant_disease`, `*_base64` variants
- `GET /fetch_object_detection_images`, `/fetch_plant_disease_images`
- `GET /get-image/<category>/<api_token>/<filename>`
