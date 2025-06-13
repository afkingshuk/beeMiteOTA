#!/usr/bin/env python3

import os
# Force OpenCV to use X11 (works on Raspberry Pi OS Bookworm)
os.environ["QT_QPA_PLATFORM"] = "xcb"

import sys
import time
import signal
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from pathlib import Path
import argparse

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description='Bee + Varroa Mite Detector (USB Camera)')
parser.add_argument('--demo', action='store_true', help='Run in demo mode with fallback video')
args = parser.parse_args()

# === CONFIGURATION ===
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_BEE_PATH = PROJECT_DIR / "Models/yolo11n_bee.pt"
MODEL_VARROA_PATH = PROJECT_DIR / "Models/yolov11_varroa.pt"
DEMO_VIDEO_PATH = PROJECT_DIR / "Videos/VARROA MITE DETECTION AND SAMPLING.mp4"
CONFIDENCE_THRESHOLD = 0.25
BEE_PADDING = 150
FRAME_SKIP = 25

# === SIGNAL HANDLER for safe camera release ===
def signal_handler(sig, frame):
    print('👋 Caught interrupt — releasing camera...')
    if 'cap' in globals() and cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === LOAD MODELS ===
print("📦 Loading YOLO models...")
bee_model = YOLO(str(MODEL_BEE_PATH))
mite_model = YOLO(str(MODEL_VARROA_PATH))
box_annotator = sv.BoxAnnotator()

print(f'✅ Bee model loaded: {MODEL_BEE_PATH.name}')
print(f'✅ Varroa model loaded: {MODEL_VARROA_PATH.name}')

# === CAMERA / VIDEO SETUP ===
frame_source = "UNKNOWN"

print("🔍 Searching for USB camera...")
CAMERA_INDEX = -1
for i in range(10):  # probe /dev/video0..9
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            CAMERA_INDEX = i
            cap.release()
            break
        else:
            cap.release()

if CAMERA_INDEX == -1:
    print("⚠️ No USB camera detected. Switching to DEMO mode.")
    args.demo = True

if args.demo:
    print("🎬 Running in DEMO mode.")
    cap = cv2.VideoCapture(str(DEMO_VIDEO_PATH))
    frame_source = "DEMO"
    if not cap.isOpened():
        print("❌ Failed to open DEMO video. Exiting.")
        sys.exit(1)
    else:
        print(f"✅ Demo video opened: {DEMO_VIDEO_PATH}")
else:
    cap = cv2.VideoCapture(CAMERA_INDEX)
    frame_source = f"USB CAMERA /dev/video{CAMERA_INDEX}"
    print(f"✅ Using USB camera index {CAMERA_INDEX} → /dev/video{CAMERA_INDEX}")

# === MAIN LOOP ===
frame_count = 0

print(f"🚀 Detection started from source [{frame_source}] (press 'q' to quit)...")

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame not read. End of video or camera error.")
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        height, width = frame.shape[:2]

        # Bee detection
        start_bee = time.time()
        detections = bee_model(frame)[0].boxes
        bee_inference_time = (time.time() - start_bee) * 1000  # ms

        # Build detections for full frame annotation
        bee_xyxy = np.array([box.xyxy[0].cpu().numpy() for box in detections], dtype=np.float32)
        if bee_xyxy.shape[0] == 0:
            bee_xyxy = np.empty((0, 4), dtype=np.float32)
        bee_conf = np.array([float(box.conf[0]) for box in detections], dtype=np.float32)
        bee_class_id = np.zeros(len(detections), dtype=int)

        detections_bees_sv = sv.Detections(
            xyxy=bee_xyxy,
            class_id=bee_class_id,
            confidence=bee_conf
        )

        if len(detections) > 0:
            print(f"✅ Bee(s) detected in frame {frame_count}: {len(detections)} bees")
        else:
            print(f"⛔ No bee detected in frame {frame_count}")

        # Annotate bee boxes first
        frame = box_annotator.annotate(frame, detections=detections_bees_sv)

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
            start_mite = time.time()
            mites = mite_model(bee_crop)[0].boxes
            mite_inference_time = (time.time() - start_mite) * 1000  # ms

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
                    print(f"🛑 MITE DETECTED in frame {frame_count}: bee crop [{x1p}:{x2p}, {y1p}:{y2p}] conf {mconf:.2f}")

            xyxy_array = np.array(mite_boxes, dtype=np.float32)
            if xyxy_array.shape[0] == 0:
                xyxy_array = np.empty((0, 4), dtype=np.float32)

            detections_sv = sv.Detections(
                xyxy=xyxy_array,
                class_id=np.zeros(len(mite_boxes), dtype=int),
                confidence=np.array(mite_confs, dtype=np.float32),
            )

            bee_crop_annotated = box_annotator.annotate(
                bee_crop.copy(), detections=detections_sv
            )

            for i, box in enumerate(mite_boxes):
                x1, y1, x2, y2 = map(int, box)
                label = f"{mite_labels[i]} ({mite_confs[i]:.2f})"
                cv2.putText(bee_crop_annotated, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Put crop back into frame
            frame[y1p:y2p, x1p:x2p] = bee_crop_annotated

            print(f"⏱️ Mite model inference time: {mite_inference_time:.2f} ms")

        # Show fully annotated frame
        cv2.imshow(f"🐝 Bee + Varroa Detector [{frame_source}]", frame)
        print(f"⏱️ Bee model inference time: {bee_inference_time:.2f} ms")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Exiting.")
            break

    except KeyboardInterrupt:
        print("👋 Interrupted by user.")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
