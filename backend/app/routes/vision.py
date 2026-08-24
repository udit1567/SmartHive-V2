import os
import tempfile
from io import BytesIO

from flask import Blueprint, current_app, request, send_from_directory

from app.auth import get_device_user

bp = Blueprint("vision", __name__)

_models = {}


def _detection_root():
    return current_app.config["DETECTION_FOLDER"]


def _load_yolo(kind):
    if kind in _models:
        return _models[kind]

    try:
        import torch
        from ultralytics import YOLO
    except ImportError:
        return None, "Vision dependencies are not installed"

    weights_key = "YOLO_OBJECT_WEIGHTS" if kind == "object" else "YOLO_PLANT_WEIGHTS"
    weights = current_app.config[weights_key]
    if not os.path.exists(weights):
        return None, f"Weights not found: {weights}"

    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _models[kind] = YOLO(weights).to(device)
    except Exception as exc:
        return None, str(exc)

    return _models[kind], None


def _extract_detections(results, model):
    detections = []
    class_counts = {}
    for result in results:
        if not hasattr(result, "boxes"):
            continue
        for box in result.boxes:
            class_name = model.names[int(box.cls)]
            confidence = round(float(box.conf), 4)
            detections.append({"class": class_name, "confidence": confidence})
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
    return detections, class_counts


def _next_image_path(category, api_token):
    folder = os.path.join(_detection_root(), category, api_token)
    os.makedirs(folder, exist_ok=True)
    existing_files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
    existing_numbers = [int(f.split(".")[0]) for f in existing_files if f.split(".")[0].isdigit()]
    next_number = max(existing_numbers, default=0) + 1
    return os.path.join(folder, f"{next_number}.jpg")


def _run_file_detection(kind, category, count_key):
    user, error = get_device_user()
    if error:
        return error

    api_token = request.headers.get("Authorization")
    if "image" not in request.files:
        return {"error": "No image provided"}, 400

    model, load_error = _load_yolo(kind)
    if load_error:
        return {"error": load_error}, 503

    image_file = request.files["image"]
    temp_path = os.path.join(tempfile.gettempdir(), image_file.filename or "upload.jpg")
    image_file.save(temp_path)
    try:
        results = model.predict(source=temp_path)
        detections, class_counts = _extract_detections(results, model)
        output_path = _next_image_path(category, api_token)
        results[0].save(output_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "counts": class_counts,
        count_key: len(detections),
        "detections": detections,
        "saved_image": output_path,
    }, 200


def _run_base64_detection(kind, category, count_key, missing_message):
    user, error = get_device_user()
    if error:
        body, status = error
        if status == 400:
            return {"error": "Missing required parameters"}, 400
        if status == 401:
            return {"error": "Invalid or missing API token"}, 401
        return error

    api_token = request.headers.get("Authorization")
    payload = request.get_json() or {}
    image_base64 = payload.get("image_base64")
    if not image_base64:
        return {"error": missing_message}, 400

    model, load_error = _load_yolo(kind)
    if load_error:
        return {"error": load_error}, 503

    try:
        import base64
        from PIL import Image

        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        temp_path = os.path.join(tempfile.gettempdir(), "temp_image.jpg")
        image.save(temp_path)
        try:
            results = model.predict(source=temp_path)
            detections, class_counts = _extract_detections(results, model)
            output_path = _next_image_path(category, api_token)
            results[0].save(output_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return {
            "counts": class_counts,
            count_key: len(detections),
            "detections": detections,
            "saved_image": output_path,
        }, 200
    except Exception as exc:
        return {"error": str(exc)}, 500


@bp.route("/detect_objects", methods=["POST"])
def detect_objects():
    return _run_file_detection("object", "object-detection", "total_objects")


@bp.route("/detect_plant_disease", methods=["POST"])
def detect_plant_disease():
    return _run_file_detection("plant", "plant-disease", "total_diseases_detected")


@bp.route("/detect_objects_base64", methods=["POST"])
def detect_objects_base64():
    return _run_base64_detection(
        "object", "object-detection", "total_objects", "Missing required parameters"
    )


@bp.route("/detect_plant_disease_base64", methods=["POST"])
def detect_plant_disease_base64():
    return _run_base64_detection(
        "plant", "plant-disease", "total_diseases_detected", "No base64 image provided"
    )


@bp.route("/fetch_object_detection_images", methods=["GET"])
def fetch_object_detection_images():
    user, error = get_device_user()
    if error:
        body, status = error
        if status == 400:
            return {"error": "Missing API token"}, 400
        if status == 401:
            return {"error": "Invalid API token"}, 401
        return error

    api_token = request.headers.get("Authorization")
    path = os.path.join(_detection_root(), "object-detection", api_token)
    if not os.path.exists(path):
        return {"object_detection_images": []}, 200

    images = [
        request.host_url + "get-image/object-detection/" + api_token + "/" + file
        for file in os.listdir(path)
        if file.endswith(".jpg")
    ]
    return {"object_detection_images": images}, 200


@bp.route("/fetch_plant_disease_images", methods=["GET"])
def fetch_plant_disease_images():
    user, error = get_device_user()
    if error:
        body, status = error
        if status == 400:
            return {"error": "Missing API token"}, 400
        if status == 401:
            return {"error": "Invalid API token"}, 401
        return error

    api_token = request.headers.get("Authorization")
    path = os.path.join(_detection_root(), "plant-disease", api_token)
    if not os.path.exists(path):
        return {"plant_disease_images": []}, 200

    images = [
        request.host_url + "get-image/plant-disease/" + api_token + "/" + file
        for file in os.listdir(path)
        if file.endswith(".jpg")
    ]
    return {"plant_disease_images": images}, 200


@bp.route("/get-image/<category>/<api_token>/<filename>", methods=["GET"])
def get_image(category, api_token, filename):
    if category not in ("object-detection", "plant-disease"):
        return {"error": "Invalid category"}, 400

    image_folder = os.path.join(_detection_root(), category, api_token)
    image_path = os.path.join(image_folder, filename)
    if not os.path.exists(image_path):
        return {"error": "Image not found"}, 404

    return send_from_directory(image_folder, filename)
