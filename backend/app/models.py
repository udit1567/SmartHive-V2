import json
from datetime import datetime

import pytz

from app.extensions import db

IST = pytz.timezone("Asia/Kolkata")


def get_ist_time():
    return datetime.now(IST)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=True)
    auth_token = db.Column(db.String(64), unique=True, nullable=True)
    telegram_bot_token = db.Column(db.String(120), nullable=True)
    telegram_chat_id = db.Column(db.String(64), nullable=True)
    watched_classes = db.Column(db.Text, nullable=True)
    gemini_api_key = db.Column(db.String(255), nullable=True)

    def get_watched_classes(self):
        if not self.watched_classes:
            return []
        try:
            return json.loads(self.watched_classes)
        except (TypeError, ValueError):
            return []

    def set_watched_classes(self, classes):
        self.watched_classes = json.dumps(list(classes)) if classes else None


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=get_ist_time)
    D1 = db.Column(db.Float, nullable=True)
    D2 = db.Column(db.Float, nullable=True)
    D3 = db.Column(db.Float, nullable=True)
    D4 = db.Column(db.Float, nullable=True)
    D5 = db.Column(db.Float, nullable=True)
    D6 = db.Column(db.Float, nullable=True)
    D7 = db.Column(db.Float, nullable=True)
    D8 = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship(
        "User", backref=db.backref("data", lazy=True, cascade="all, delete-orphan")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%d %B %Y %H:%M"),
            "D1": self.D1,
            "D2": self.D2,
            "D3": self.D3,
            "D4": self.D4,
            "D5": self.D5,
            "D6": self.D6,
            "D7": self.D7,
            "D8": self.D8,
            "user_id": self.user_id,
        }


class PlantDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=get_ist_time)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    total_detected = db.Column(db.Integer, nullable=False, default=0)
    classes = db.Column(db.Text, nullable=True)
    user = db.relationship(
        "User", backref=db.backref("plant_detections", lazy=True, cascade="all, delete-orphan")
    )

    def get_classes(self):
        if not self.classes:
            return []
        try:
            return json.loads(self.classes)
        except (TypeError, ValueError):
            return []

    def set_classes(self, detections):
        self.classes = json.dumps(detections) if detections else None

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%d %B %Y %H:%M"),
            "imageUrl": self.image_url,
            "totalDetected": self.total_detected,
            "classes": self.get_classes(),
        }


class ChatThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False, default="New chat")
    created_at = db.Column(db.DateTime, nullable=False, default=get_ist_time)
    updated_at = db.Column(db.DateTime, nullable=False, default=get_ist_time, onupdate=get_ist_time)
    user = db.relationship(
        "User", backref=db.backref("chat_threads", lazy=True, cascade="all, delete-orphan")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "createdAt": self.created_at.strftime("%d %B %Y %H:%M"),
            "updatedAt": self.updated_at.strftime("%d %B %Y %H:%M"),
        }


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey("chat_thread.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_ist_time)
    thread = db.relationship(
        "ChatThread",
        backref=db.backref(
            "messages", lazy=True, cascade="all, delete-orphan", order_by="ChatMessage.created_at"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "imageUrl": self.image_url,
            "createdAt": self.created_at.strftime("%d %B %Y %H:%M"),
        }
