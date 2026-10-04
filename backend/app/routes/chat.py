from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import ChatMessage, ChatThread, User, get_ist_time

bp = Blueprint("chat", __name__, url_prefix="/chat")

_TITLE_MAX_LENGTH = 60


def _current_user():
    email = get_jwt_identity()
    if not email:
        return None
    return User.query.filter_by(email=email).first()


def _get_owned_thread(thread_id, user):
    return ChatThread.query.filter_by(id=thread_id, user_id=user.id).first()


@bp.route("/threads", methods=["GET"])
@jwt_required()
def list_threads():
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    threads = (
        ChatThread.query.filter_by(user_id=user.id).order_by(ChatThread.updated_at.desc()).all()
    )
    return jsonify({"threads": [t.to_dict() for t in threads]}), 200


@bp.route("/threads", methods=["POST"])
@jwt_required()
def create_thread():
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip() or "New chat"
    thread = ChatThread(user_id=user.id, title=title)
    db.session.add(thread)
    db.session.commit()
    return jsonify(thread.to_dict()), 201


@bp.route("/threads/<int:thread_id>", methods=["GET"])
@jwt_required()
def get_thread(thread_id):
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    thread = _get_owned_thread(thread_id, user)
    if not thread:
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify(
        {"thread": thread.to_dict(), "messages": [m.to_dict() for m in thread.messages]}
    ), 200


@bp.route("/threads/<int:thread_id>", methods=["DELETE"])
@jwt_required()
def delete_thread(thread_id):
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    thread = _get_owned_thread(thread_id, user)
    if not thread:
        return jsonify({"error": "Conversation not found"}), 404

    db.session.delete(thread)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@bp.route("/threads/<int:thread_id>/messages", methods=["POST"])
@jwt_required()
def add_message(thread_id):
    user = _current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    thread = _get_owned_thread(thread_id, user)
    if not thread:
        return jsonify({"error": "Conversation not found"}), 404

    data = request.get_json(silent=True) or {}
    role = data.get("role")
    content = data.get("content")
    if role not in ("user", "assistant") or not content:
        return jsonify({"error": "role and content are required"}), 400

    message = ChatMessage(
        thread_id=thread.id,
        role=role,
        content=content,
        image_url=data.get("imageUrl") or None,
    )
    db.session.add(message)

    if role == "user" and thread.title == "New chat":
        thread.title = content[:_TITLE_MAX_LENGTH] + ("…" if len(content) > _TITLE_MAX_LENGTH else "")

    thread.updated_at = get_ist_time()
    db.session.commit()

    return jsonify(message.to_dict()), 201
