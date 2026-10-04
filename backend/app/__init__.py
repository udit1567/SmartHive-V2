import os

from flask import Flask, send_from_directory
from sqlalchemy import inspect, text

from app.config import Config
from app.extensions import cors, db, jwt
from app.models import ChatMessage, ChatThread, Data, PlantDetection, User  # noqa: F401
from app.routes.auth import bp as auth_bp
from app.routes.chat import bp as chat_bp
from app.routes.sensors import bp as sensors_bp
from app.routes.vision import bp as vision_bp

_NEW_USER_COLUMNS = {
    "telegram_bot_token": "VARCHAR(120)",
    "telegram_chat_id": "VARCHAR(64)",
    "watched_classes": "TEXT",
    "gemini_api_key": "VARCHAR(255)",
}


def _ensure_user_columns():
    """Add columns introduced after a User table already exists on disk.

    db.create_all() only creates missing tables, so existing SQLite databases
    need these columns patched in by hand.
    """
    existing = {col["name"] for col in inspect(db.engine).get_columns("user")}
    for column, ddl_type in _NEW_USER_COLUMNS.items():
        if column not in existing:
            db.session.execute(text(f"ALTER TABLE user ADD COLUMN {column} {ddl_type}"))
    db.session.commit()


def _register_frontend(app):
    """Serve the built Vue app (frontend/dist) from the same origin as the API.

    Routing is hash-based, so only real files need serving — no SPA fallback.
    API routes are more specific than the catch-all and still take precedence.
    """
    dist = app.config["FRONTEND_DIST"]
    has_build = os.path.isfile(os.path.join(dist, "index.html"))

    @app.get("/")
    def index():
        if has_build:
            return send_from_directory(dist, "index.html")
        return "hello from index page"

    if has_build:

        @app.get("/<path:filename>")
        def frontend_file(filename):
            return send_from_directory(dist, filename)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = True

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(sensors_bp)
    app.register_blueprint(vision_bp)
    _register_frontend(app)

    with app.app_context():
        db.create_all()
        _ensure_user_columns()

    return app
