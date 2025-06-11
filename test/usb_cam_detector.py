#!/usr/bin/env python3

import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

# CONFIGURATION
MODEL_BEE_PATH = "Models/yolo11n_bee.pt"
MODEL_VARROA_PATH = "Models/yolov11_varroa.pt"
CONFIDENCE_THRESHOLD = 0.25
BEE_PADDING = 150

# Load models
print("📦 Loading YOLO models...")
bee_model = YOLO(MODEL_BEE_PATH)
mite_model = YOLO(MODEL_VARROA_PATH)
box_annotator = sv.BoxAnnotator()

# Find USB camera
print("🔍 Searching for USB camera...")
CAMERA_INDEX = -1
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ USB camera found at index {i}")
        CAMERA_INDEX = i
        cap.release()
        break

if CAMERA_INDEX == -1:
    print("❌ No USB camera detected.")
    exit(1)

# Open camera
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("❌ Failed to open USB camera.")
    exit(1)

print("🚀 Starting detection (press 'q' to quit)...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame.")
        break

    height, width = frame.shape[:2]
    bee_detections = bee_model(frame)[0].boxes

    for box in bee_detections:
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
        mite_boxes = []
        mite_labels = []
        mite_confs = []
        mites = mite_model(bee_crop)[0].boxes

        for mbox in mites:
            mx1, my1, mx2, my2 = map(int, mbox.xyxy[0])
            mconf = float(mbox.conf[0])
            if mconf >= CONFIDENCE_THRESHOLD:
                mite_boxes.append([mx1, my1, mx2, my2])
                mite_labels.append("Varroa")
                mite_confs.append(mconf)

        # Annotate bee crop
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

        # Put crop back in frame
        frame[y1p:y2p, x1p:x2p] = bee_crop_annotated

    cv2.imshow("🐝 Bee + Varroa USB Camera Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting.")
        break

cap.release()
cv2.destroyAllWindows()
