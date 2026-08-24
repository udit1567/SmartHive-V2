from flask import Flask

from app.config import Config
from app.extensions import cors, db, jwt
from app.models import Data, User  # noqa: F401
from app.routes.auth import bp as auth_bp
from app.routes.sensors import bp as sensors_bp
from app.routes.vision import bp as vision_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = True

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(sensors_bp)
    app.register_blueprint(vision_bp)

    with app.app_context():
        db.create_all()

    return app
