import cv2
import time
import numpy as np
from ultralytics import YOLO
import supervision as sv
from picamera2 import Picamera2

# === CONFIG ===
BEE_MODEL_PATH = "Models/yolo11n_bee.pt"
VARROA_MODEL_PATH = "Models/yolov11_varroa.pt"
CONFIDENCE_THRESHOLD = 0.4
CROP_PADDING = 20  # breathing room for cropping

# === INIT MODELS ===
print("📦 Loading models...")
bee_model = YOLO(BEE_MODEL_PATH)
mite_model = YOLO(VARROA_MODEL_PATH)

# === INIT CAMERA ===
print("📷 Starting PiCamera...")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()
time.sleep(2)

# === LIVE LOOP ===
print("🚀 Running live detection. Press 'q' to quit.")
annotator = sv.BoxAnnotator()

while True:
    frame = picam2.capture_array()
    display_frame = frame.copy()

    # Step 1: Detect Bees
    bee_results = bee_model(frame, verbose=False)[0]
    bee_detections = bee_results.boxes

    for i, bee_box in enumerate(bee_detections):
        x1, y1, x2, y2 = map(int, bee_box.xyxy[0])
        h, w, _ = frame.shape
        x1p = max(x1 - CROP_PADDING, 0)
        y1p = max(y1 - CROP_PADDING, 0)
        x2p = min(x2 + CROP_PADDING, w)
        y2p = min(y2 + CROP_PADDING, h)

        bee_crop = frame[y1p:y2p, x1p:x2p]

        # Step 2: Detect Mites on the cropped bee
        mite_result = mite_model.predict(source=bee_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
        mite_boxes = mite_result.boxes

        # Adjust mite box positions relative to full frame
        for j, mbox in enumerate(mite_boxes):
            mx1, my1, mx2, my2 = map(int, mbox.xyxy[0])
            mx1 += x1p
            mx2 += x1p
            my1 += y1p
            my2 += y1p

            # Draw mite boxes in red
            cv2.rectangle(display_frame, (mx1, my1), (mx2, my2), (0, 0, 255), 2)
            cv2.putText(display_frame, f"mite {mbox.conf[0]:.2f}", (mx1, my1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Draw bee box in green
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display_frame, f"bee {bee_box.conf[0]:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Show result on screen
    cv2.imshow("🐝 Bee & Varroa Detector", display_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()
