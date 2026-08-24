import json
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)

from app.auth import generate_auth_token, hash_password, verify_password
from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__)


@bp.route("/")
def index():
    return "hello from index page"


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and verify_password(user.password, password):
        access_token = create_access_token(identity=email)
        return jsonify(
            {
                "email": user.email,
                "access_token": access_token,
                "uid": user.id,
                "auth_token": user.auth_token,
            }
        ), 200

    return jsonify({"message": "Invalid credentials!"}), 401


@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    password = data.get("password")
    address = data.get("address")
    source = data.get("source")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists!"}), 400

    new_user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=hash_password(password),
        address=address,
        source=source,
        auth_token=generate_auth_token(),
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful!", "auth_token": new_user.auth_token}), 201


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@bp.route("/profile/<string:getemail>", methods=["GET"])
@jwt_required()
def my_profile(getemail):
    current_user_email = get_jwt_identity()
    if not current_user_email or current_user_email != getemail:
        return jsonify({"error": "Unauthorized Access"}), 401

    user = User.query.filter_by(email=getemail).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(
        {
            "id": user.id,
            "name": user.first_name,
            "email": user.email,
            "token": user.auth_token,
        }
    ), 200


@bp.after_app_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if isinstance(data, dict):
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        return response
