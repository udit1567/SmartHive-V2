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

WORKDIR /app/backend

# Vision/AI (torch + ultralytics) is intentionally not installed here — it
# needs more RAM than Render's free tier and adds ~2.5 GB to the image. The
# /detect_* routes return 503; auth + sensors run normally. See
# backend/requirements.txt to enable vision locally.
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt gunicorn==23.0.0

# Backend source
COPY backend/ ./

# Built frontend, at the path Config.FRONTEND_DIST resolves to by default
COPY --from=frontend /frontend/dist /app/frontend/dist

# App state lives in /data. On Render's free tier there is no persistent disk,
# so this is ephemeral and the SQLite DB resets on each deploy/restart; attach
# a disk (paid plan) at /data to make it persist.
ENV HOST=0.0.0.0 \
    PORT=5000 \
    DATABASE_URI=sqlite:////data/smarthive.sqlite3 \
    DETECTION_FOLDER=/data/detections
RUN mkdir -p /data/detections

EXPOSE 5000

# One worker: live-stream state is cached in-process, so extra workers would
# each keep their own copy. Threads handle concurrency; timeout 0 keeps
# long-lived MJPEG streams from being killed.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 8 --worker-class gthread --timeout 0 run:app"]
