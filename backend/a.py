import os
import cv2
from ultralytics import YOLO

# =====================================================
# ESP32-CAM STREAM
# =====================================================

ESP32_IP = "192.168.1.21"   # <-- CHANGE THIS
STREAM_URL = f"http://{ESP32_IP}/stream"

# =====================================================
# YOLO26
# =====================================================

MODEL_PATH = "yolo26n.pt"

print("Loading YOLO26...")

# If yolo26n.pt is not present, Ultralytics
# automatically downloads it.
model = YOLO(MODEL_PATH)

print("YOLO26 ready")

# =====================================================
# OPEN ESP32-CAM STREAM
# =====================================================

print(f"Connecting to {STREAM_URL}...")

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("ERROR: Could not connect to ESP32-CAM")
    print(f"Check that this works in your browser:")
    print(STREAM_URL)
    exit()

print("ESP32-CAM connected")
print("Press Q to quit")

# =====================================================
# LIVE DETECTION
# =====================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        continue

    # Run YOLO26
    results = model.predict(
        frame,
        imgsz=640,
        conf=0.4,
        verbose=False
    )

    # Draw bounding boxes
    annotated_frame = results[0].plot()

    # Show live feed
    cv2.imshow(
        "ESP32-CAM + YOLO26",
        annotated_frame
    )

    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# =====================================================
# CLEANUP
# =====================================================

cap.release()
cv2.destroyAllWindows()