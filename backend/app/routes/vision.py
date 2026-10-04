import base64
import os
import tempfile
import threading
import time
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import urlparse

from flask import Blueprint, Response, current_app, request, send_from_directory

from app.auth import get_device_user
from app.extensions import db
from app.models import PlantDetection
from app.notify import notify_telegram_async, notify_telegram_photo_async

bp = Blueprint("vision", __name__)

_models = {}
_model_load_lock = threading.Lock()

# Fallback so the frontend can populate a class picker before YOLO weights
# are on disk (standard YOLOv8 / COCO 80-class order).
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
]

_NOTIFY_DEBOUNCE_SECONDS = 30
_last_notified = {}


def _maybe_notify_telegram(user, kind, class_counts, get_image_bytes=None):
    if kind != "object" or not class_counts:
        return
    if not user.telegram_bot_token or not user.telegram_chat_id:
        return

    watched = set(user.get_watched_classes())
    matched = sorted(watched.intersection(class_counts))
    if not matched:
        return

    now = time.monotonic()
    if now - _last_notified.get(user.id, 0.0) < _NOTIFY_DEBOUNCE_SECONDS:
        return
    _last_notified[user.id] = now

    lines = [f"{name} x{class_counts[name]}" for name in matched]
    message = (
        "\U0001f41d SmartHive detection alert\n"
        + "\n".join(lines)
        + f"\n{datetime.now(timezone.utc).isoformat()}"
    )

    image_bytes = get_image_bytes() if get_image_bytes else None
    if image_bytes:
        notify_telegram_photo_async(user.telegram_bot_token, user.telegram_chat_id, image_bytes, message)
    else:
        notify_telegram_async(user.telegram_bot_token, user.telegram_chat_id, message)


def _read_image_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def _encode_annotated_jpeg(results, quality=80):
    """Renders boxes/labels onto the frame in memory (no disk write) —
    used by endpoints that intentionally don't persist frames, and to
    return a preview for the live webpage view."""
    try:
        import cv2
    except ImportError:
        return None

    annotated = results[0].plot()
    encoded, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not encoded:
        return None
    return buf.tobytes()


def _detection_root():
    return current_app.config["DETECTION_FOLDER"]


def _load_yolo(kind):
    cached = _models.get(kind)
    if cached is not None:
        return cached, None

    try:
        import torch
        from ultralytics import YOLO
    except ImportError:
        return None, "Vision dependencies are not installed"

    weights_key = "YOLO_OBJECT_WEIGHTS" if kind == "object" else "YOLO_PLANT_WEIGHTS"
    weights = current_app.config[weights_key]
    if not os.path.exists(weights):
        return None, f"Weights not found: {weights}"

    with _model_load_lock:
        cached = _models.get(kind)
        if cached is not None:
            return cached, None

        # ultralytics strips apostrophes from the path it's given before
        # checking it exists (attempt_download_asset), which breaks any
        # absolute path containing one (e.g. a macOS home dir like
        # "Udit's"). Load by bare filename with cwd set to its folder so
        # ultralytics never sees a path segment to mangle.
        weights_dir, weights_name = os.path.split(weights)
        previous_cwd = os.getcwd()
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            os.chdir(weights_dir)
            _models[kind] = YOLO(weights_name).to(device)
        except Exception as exc:
            return None, str(exc)
        finally:
            os.chdir(previous_cwd)

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
            xyxy = box.xyxy[0].tolist()
            detections.append(
                {
                    "class": class_name,
                    "confidence": confidence,
                    "box": [round(float(v), 1) for v in xyxy],
                }
            )
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
    return detections, class_counts


def _next_image_path(category, api_token):
    folder = os.path.join(_detection_root(), category, api_token)
    os.makedirs(folder, exist_ok=True)
    existing_files = [f for f in os.listdir(folder) if f.endswith(".jpg")]
    existing_numbers = [int(f.split(".")[0]) for f in existing_files if f.split(".")[0].isdigit()]
    next_number = max(existing_numbers, default=0) + 1
    return os.path.join(folder, f"{next_number}.jpg")


def _save_plant_detection_history(user, api_token, output_path, detections):
    filename = os.path.basename(output_path)
    image_url = request.host_url + "get-image/plant-disease/" + api_token + "/" + filename
    record = PlantDetection(user_id=user.id, image_url=image_url, total_detected=len(detections))
    record.set_classes(detections)
    db.session.add(record)
    db.session.commit()


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

    _maybe_notify_telegram(user, kind, class_counts, get_image_bytes=lambda: _read_image_bytes(output_path))
    if category == "plant-disease":
        _save_plant_detection_history(user, api_token, output_path, detections)

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

        _maybe_notify_telegram(
            user, kind, class_counts, get_image_bytes=lambda: _read_image_bytes(output_path)
        )
        if category == "plant-disease":
            _save_plant_detection_history(user, api_token, output_path, detections)

        return {
            "counts": class_counts,
            count_key: len(detections),
            "detections": detections,
            "saved_image": output_path,
        }, 200
    except Exception as exc:
        return {"error": str(exc)}, 500


def _run_live_detection(kind, count_key):
    user, error = get_device_user()
    if error:
        return error

    model, load_error = _load_yolo(kind)
    if load_error:
        return {"error": load_error}, 503

    image_bytes = None
    if "image" in request.files:
        image_bytes = request.files["image"].read()
    else:
        payload = request.get_json(silent=True) or {}
        image_base64 = payload.get("image_base64")
        if image_base64:
            image_bytes = base64.b64decode(image_base64)

    if not image_bytes:
        return {"error": "Send a webcam frame or a base64 image"}, 400

    temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    temp_path = temp.name
    temp.write(image_bytes)
    temp.close()
    try:
        results = model.predict(source=temp_path, verbose=False)
        detections, class_counts = _extract_detections(results, model)
        shape = getattr(results[0], "orig_shape", (0, 0))
        height, width = int(shape[0]), int(shape[1])
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    _maybe_notify_telegram(
        user, kind, class_counts, get_image_bytes=lambda: _encode_annotated_jpeg(results)
    )

    return {
        "counts": class_counts,
        count_key: len(detections),
        "detections": detections,
        "width": width,
        "height": height,
        "live": True,
    }, 200


class _LatestFrameCapture:
    """Continuously drains a cv2.VideoCapture on a background thread and keeps
    only the newest frame. Without this, a slow consumer (YOLO inference)
    falls behind cv2's internal read buffer and the stream's lag grows
    without bound; this way a slow consumer just skips stale frames instead.
    """

    def __init__(self, cap):
        self._cap = cap
        self._frame = None
        self._lock = threading.Lock()
        self._stopped = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stopped:
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.02)
                continue
            with self._lock:
                self._frame = frame

    def read(self):
        with self._lock:
            return self._frame

    def stop(self):
        self._stopped = True
        self._thread.join(timeout=1)
        self._cap.release()


def _mjpeg_frames(reader, model, user, kind):
    import cv2

    consecutive_empty = 0
    try:
        while True:
            frame = reader.read()
            if frame is None:
                consecutive_empty += 1
                if consecutive_empty > 200:
                    break
                time.sleep(0.02)
                continue
            consecutive_empty = 0

            results = model.predict(frame, verbose=False)
            annotated = results[0].plot()
            encoded, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not encoded:
                continue

            _, class_counts = _extract_detections(results, model)
            payload = buf.tobytes()
            _maybe_notify_telegram(user, kind, class_counts, get_image_bytes=lambda: payload)

            header = (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(payload)).encode("ascii") + b"\r\n\r\n"
            )
            yield header + payload + b"\r\n"
    finally:
        reader.stop()


def _run_stream_detection(kind):
    user, error = get_device_user()
    if error:
        return error

    source_url = (request.args.get("source_url") or "").strip()
    parsed = urlparse(source_url)
    if parsed.scheme not in ("http", "https"):
        return {"error": "source_url must start with http:// or https://"}, 400

    model, load_error = _load_yolo(kind)
    if load_error:
        return {"error": load_error}, 503

    try:
        import cv2
    except ImportError:
        return {"error": "Vision dependencies are not installed"}, 503

    cap = cv2.VideoCapture(source_url)
    if not cap.isOpened():
        cap.release()
        return {"error": f"Could not open camera stream: {source_url}"}, 400

    reader = _LatestFrameCapture(cap)

    return Response(
        _mjpeg_frames(reader, model, user, kind),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@bp.route("/stream_live_objects", methods=["GET"])
def stream_live_objects():
    return _run_stream_detection("object")


@bp.route("/stream_live_plant_disease", methods=["GET"])
def stream_live_plant_disease():
    return _run_stream_detection("plant")


@bp.route("/object_classes", methods=["GET"])
def object_classes():
    model, _load_error = _load_yolo("object")
    names = sorted(model.names.values()) if model is not None else COCO_CLASSES
    return {"classes": names}, 200


@bp.route("/detect_live_objects", methods=["POST"])
def detect_live_objects():
    return _run_live_detection("object", "total_objects")


@bp.route("/detect_live_plant_disease", methods=["POST"])
def detect_live_plant_disease():
    return _run_live_detection("plant", "total_diseases_detected")


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


@bp.route("/plant_detections", methods=["GET"])
def plant_detections():
    user, error = get_device_user()
    if error:
        return error

    records = (
        PlantDetection.query.filter_by(user_id=user.id)
        .order_by(PlantDetection.timestamp.desc())
        .limit(50)
        .all()
    )
    return {"plant_detections": [record.to_dict() for record in records]}, 200


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
