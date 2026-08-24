import secrets
import string

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User


def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)


def generate_auth_token(length=8):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def get_device_user():
    """Look up the device user from the Authorization header (legacy auth_token)."""
    api_token = request.headers.get("Authorization")
    if not api_token:
        return None, ({"message": "Missing required parameters"}, 400)

    user = User.query.filter_by(auth_token=api_token).first()
    if not user:
        return None, ({"message": "Invalid or missing API token"}, 401)

    return user, None
