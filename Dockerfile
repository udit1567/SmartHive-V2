# syntax=docker/dockerfile:1
# SmartHive V2 — single container: Vue frontend is built, then served by Flask
# (gunicorn) on the same origin as the API.
#
#   docker build -t smarthive .
#   docker run -p 5000:5000 -v smarthive-data:/data \
#     -e SECRET_KEY=... -e JWT_SECRET_KEY=... smarthive
#
# On Render this is deployed via render.yaml (PORT is injected by Render).

# ---------- Stage 1: build the frontend ----------
FROM node:20-slim AS frontend
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Empty API base URL => the browser calls the API on the same origin it loaded
# the page from, so the image works behind any host/port/domain.
ENV VITE_API_URL=""
RUN npm run build

# ---------- Stage 2: backend runtime ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# OpenCV (pulled in by ultralytics) needs these shared libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# CPU-only torch first — the default PyPI wheels bundle CUDA and add ~2.5 GB.
RUN pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.6.0 torchvision==0.21.0
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt gunicorn==23.0.0

# Backend source (+ any *.pt weights present in backend/)
COPY backend/ ./

# *.pt files are gitignored, so builds from git (e.g. Render) have none.
# Download any that are missing. Render passes env vars of the same name as
# build args; leave a URL empty to skip it (vision routes then return 503).
ARG YOLO_OBJECT_WEIGHTS_URL=https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8l.pt
ARG YOLO_PLANT_WEIGHTS_URL=""
RUN python - <<PY
import os, urllib.request
for name, url in (("yolov8l.pt", "${YOLO_OBJECT_WEIGHTS_URL}"), ("best.pt", "${YOLO_PLANT_WEIGHTS_URL}")):
    if url and not os.path.exists(name):
        print(f"Downloading {name} from {url}")
        urllib.request.urlretrieve(url, name)
PY
# Built frontend, at the path Config.FRONTEND_DIST resolves to by default
COPY --from=frontend /frontend/dist /app/frontend/dist

# Persistent state lives in /data — mount a volume / Render disk there.
ENV HOST=0.0.0.0 \
    PORT=5000 \
    DATABASE_URI=sqlite:////data/smarthive.sqlite3 \
    DETECTION_FOLDER=/data/detections \
    YOLO_CONFIG_DIR=/data/ultralytics
RUN mkdir -p /data/detections /data/ultralytics

EXPOSE 5000

# One worker: YOLO models and live-stream state are cached in-process, so
# extra workers would each load their own copy. Threads handle concurrency;
# timeout 0 keeps long-lived MJPEG streams from being killed.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 8 --worker-class gthread --timeout 0 run:app"]
