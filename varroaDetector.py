#!/usr/bin/env python3

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"

import sys
import time
import signal
import csv
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from pathlib import Path
import argparse
import Adafruit_DHT
from datetime import datetime

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description='Bee + Varroa Mite Detector + DHT22 Logger')
parser.add_argument('--no-retry', action='store_true', help='Do not retry if no camera found (exit)')
args = parser.parse_args()

# === CONFIGURATION ===
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_BEE_PATH = PROJECT_DIR / "Models/yolo11n_bee.pt"
MODEL_VARROA_PATH = PROJECT_DIR / "Models/yolov11_varroa.pt"
CONFIDENCE_THRESHOLD = 0.25
BEE_PADDING = 150
FRAME_SKIP = 25
LOG_DIR = PROJECT_DIR / "beeMite_logs"
LOG_CSV = LOG_DIR / "bee_mite_log.csv"

# DHT22 Config
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 26  # GPIO26 → pin 32

# === SIGNAL HANDLER ===
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

# === INIT LOGGING ===
os.makedirs(LOG_DIR, exist_ok=True)

if not LOG_CSV.exists():
    with open(LOG_CSV, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "temp_C", "humidity_pct", "bee_count", "mite_count"])
    print(f'✅ CSV log initialized at: {LOG_CSV}')
else:
    print(f'✅ Logging to existing CSV: {LOG_CSV}')

# === CAMERA PROBE LOOP ===
CAMERA_INDEX = -1
cap = None
frame_source = "USB CAMERA"

while True:
    print("🔍 Searching for USB camera...")
    CAMERA_INDEX = -1
    for i in range(10):
        temp_cap = cv2.VideoCapture(i)
        if temp_cap.isOpened():
            ret, frame = temp_cap.read()
            if ret:
                CAMERA_INDEX = i
                temp_cap.release()
                break
            else:
                temp_cap.release()

    if CAMERA_INDEX == -1:
        print("⚠️ No USB camera detected.")
        if args.no_retry:
            print("❌ Exiting because --no-retry was specified.")
            sys.exit(1)
        else:
            print("⏳ Retrying in 3 seconds...")
            time.sleep(3)
            continue
    else:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        print(f"✅ Using USB camera index {CAMERA_INDEX} → /dev/video{CAMERA_INDEX}")
        break

# === MAIN LOOP ===
frame_count = 0

print(f"🚀 Detection started from source [{frame_source} /dev/video{CAMERA_INDEX}] (press 'q' to quit)...")

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame not read. Camera may be disconnected.")
            cap.release()

            if args.no_retry:
                print("❌ Exiting because --no-retry was specified.")
                sys.exit(1)

            print("⏳ Retrying camera connection...")
            while True:
                CAMERA_INDEX = -1
                for i in range(10):
                    temp_cap = cv2.VideoCapture(i)
                    if temp_cap.isOpened():
                        ret, frame = temp_cap.read()
                        if ret:
                            CAMERA_INDEX = i
                            temp_cap.release()
                            break
                        else:
                            temp_cap.release()

                if CAMERA_INDEX == -1:
                    print("⚠️ No USB camera detected. Retrying in 3 seconds...")
                    time.sleep(3)
                    continue
                else:
                    cap = cv2.VideoCapture(CAMERA_INDEX)
                    print(f"✅ Reconnected to USB camera index {CAMERA_INDEX} → /dev/video{CAMERA_INDEX}")
                    break
            continue

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        height, width = frame.shape[:2]

        # Read DHT22
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is None or temperature is None:
            temp_C = "NaN"
            humidity_pct = "NaN"
            print("⚠️ Failed to read DHT22 sensor.")
        else:
            temp_C = round(temperature, 2)
            humidity_pct = round(humidity, 2)
            print(f"🌡️ Temp: {temp_C}°C  💧 Humidity: {humidity_pct}%")

        # Bee detection
        start_bee = time.time()
        detections = bee_model(frame)[0].boxes
        bee_inference_time = (time.time() - start_bee) * 1000  # ms

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

        bee_count = len(detections)
        mite_count = 0

        if bee_count > 0:
            print(f"✅ Bee(s) detected in frame {frame_count}: {bee_count} bees")
        else:
            print(f"⛔ No bee detected in frame {frame_count}")

        frame = box_annotator.annotate(frame, detections=detections_bees_sv)

        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            if conf < CONFIDENCE_THRESHOLD:
                continue

            x1p = max(0, x1 - BEE_PADDING)
            y1p = max(0, y1 - BEE_PADDING)
            x2p = min(width, x2 + BEE_PADDING)
            y2p = min(height, y2 + BEE_PADDING)

            bee_crop = frame[y1p:y2p, x1p:x2p]

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
                    mite_count += 1
                    print(f"🛑 MITE DETECTED in frame {frame_count} conf {mconf:.2f}")

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

            frame[y1p:y2p, x1p:x2p] = bee_crop_annotated

            print(f"⏱️ Mite model inference time: {mite_inference_time:.2f} ms")

        # Log CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_CSV, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, temp_C, humidity_pct, bee_count, mite_count])

        # Show frame
        cv2.imshow(f"🐝 Bee + Varroa Detector + DHT22 [{frame_source} /dev/video{CAMERA_INDEX}]", frame)
        print(f"⏱️ Bee model inference time: {bee_inference_time:.2f} ms")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Exiting.")
            break

    except KeyboardInterrupt:
        print("👋 Interrupted by user.")
        break

cap.release()
cv2.destroyAllWindows()
