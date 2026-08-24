import os
from datetime import timedelta

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _path(env_key, default):
    value = os.environ.get(env_key, default)
    if os.path.isabs(value):
        return value
    return os.path.join(_BACKEND_ROOT, value)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me-too")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///build.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    YOLO_OBJECT_WEIGHTS = _path("YOLO_OBJECT_WEIGHTS", "yolov8l.pt")
    YOLO_PLANT_WEIGHTS = _path("YOLO_PLANT_WEIGHTS", "best.pt")
    DETECTION_FOLDER = _path("DETECTION_FOLDER", "Detection images")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
