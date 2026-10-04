import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
from io import BytesIO


def send_telegram_message(bot_token, chat_id, message):
    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except (urllib.error.URLError, OSError) as exc:
        print("[TELEGRAM ERROR]", repr(exc))


def send_telegram_photo(bot_token, chat_id, photo_bytes, caption=""):
    if not bot_token or not chat_id or not photo_bytes:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    boundary = uuid.uuid4().hex

    body = BytesIO()
    for name, value in (("chat_id", chat_id), ("caption", caption)):
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.write(f"{value}\r\n".encode("utf-8"))
    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(b'Content-Disposition: form-data; name="photo"; filename="detection.jpg"\r\n')
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(photo_bytes)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=body.getvalue(),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except (urllib.error.URLError, OSError) as exc:
        print("[TELEGRAM ERROR]", repr(exc))


def notify_telegram_async(bot_token, chat_id, message):
    threading.Thread(
        target=send_telegram_message,
        args=(bot_token, chat_id, message),
        daemon=True,
    ).start()


def notify_telegram_photo_async(bot_token, chat_id, photo_bytes, caption=""):
    threading.Thread(
        target=send_telegram_photo,
        args=(bot_token, chat_id, photo_bytes, caption),
        daemon=True,
    ).start()
