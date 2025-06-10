import os
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from pathlib import Path
import argparse

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description='Bee + Varroa Mite Detector')
parser.add_argument('--demo', action='store_true', help='Run in demo mode with fallback video')
args = parser.parse_args()

# === CONFIGURATION ===
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_BEE_PATH = PROJECT_DIR / "Models/yolo11n_bee.pt"
MODEL_VARROA_PATH = PROJECT_DIR / "Models/yolov11_varroa.pt"
DEMO_VIDEO_PATH = PROJECT_DIR / "video/sample_video.mp4"
CAMERA_INDEX = 0
FRAME_SKIP = 5
CONFIDENCE_THRESHOLD = 0.25
BEE_PADDING = 10

# === LOAD MODELS ===
print("📦 Loading YOLO models...")
bee_model = YOLO(str(MODEL_BEE_PATH))
mite_model = YOLO(str(MODEL_VARROA_PATH))
box_annotator = sv.BoxAnnotator()

# === CAMERA DETECTION ===
USE_CAMERA = not args.demo
if USE_CAMERA:
    print("🔍 Trying to open camera...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("⚠️ Camera not detected — switching to demo mode.")
        USE_CAMERA = False
        cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))
else:
    print("🎬 Running in demo mode.")
    cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))

# === MAIN LOOP ===
frame_count = 0
recent_frames = []

print("🚀 Detection started (press 'q' to quit)...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not read. End of video or camera error.")
        break

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    original = frame.copy()
    height, width = frame.shape[:2]
    detections = bee_model(frame)[0].boxes

    for box in detections:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])

        if conf < CONFIDENCE_THRESHOLD:
            continue

        # Pad crop
        x1p = max(0, x1 - BEE_PADDING)
        y1p = max(0, y1 - BEE_PADDING)
        x2p = min(width, x2 + BEE_PADDING)
        y2p = min(height, y2 + BEE_PADDING)

        bee_crop = frame[y1p:y2p, x1p:x2p]

        # Mite detection
        mites = mite_model(bee_crop)[0].boxes
        mite_boxes = []
        mite_labels = []
        mite_confs = []

        for mbox in mites:
            mx1, my1, mx2, my2 = map(int, mbox.xyxy[0])
            mconf = float(mbox.conf[0])
            if mconf >= CONFIDENCE_THRESHOLD:
                mite_boxes.append([mx1, my1, mx2, my2])
                mite_labels.append("Varroa")
                mite_confs.append(mconf)

        # Annotate bee crop with mite detections
        detections_sv = sv.Detections(
            xyxy=np.array(mite_boxes),
            class_id=np.zeros(len(mite_boxes), dtype=int),
            confidence=np.array(mite_confs),
        )

        bee_crop_annotated = box_annotator.annotate(
            bee_crop.copy(), detections=detections_sv, labels=mite_labels
        )

        # Put crop back into frame
        frame[y1p:y2p, x1p:x2p] = bee_crop_annotated

    # Show frame
    cv2.imshow("🐝 Bee + Varroa Detector", frame)

    # Keep last 10 frames
    recent_frames = (recent_frames + [frame.copy()])[-10:]

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting.")
        break

cap.release()
cv2.destroyAllWindows()
