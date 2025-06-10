import os
import sys

# Setup and check required packages
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_DIR)
from check_imports import check_and_install_requirements
check_and_install_requirements(os.path.join(PROJECT_DIR, "requirements.txt"))

# Now safe to import rest of modules
import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from pathlib import Path
import argparse
import matplotlib.pyplot as plt
# Optional PiCamera2 (commented — enable if you want real PiCam feed)
# from picamera2 import Picamera2

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description='Bee + Varroa Mite Detector')
parser.add_argument('--demo', action='store_true', help='Run in demo mode with fallback video')
parser.add_argument('--picamera', action='store_true', help='Run with Raspberry Pi Camera (PiCamera2)')
args = parser.parse_args()

# === CONFIGURATION ===
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_BEE_PATH = PROJECT_DIR / "Models/yolo11n_bee.pt"
MODEL_VARROA_PATH = PROJECT_DIR / "Models/yolov11_varroa.pt"
DEMO_VIDEO_PATH = PROJECT_DIR / "Videos/VARROA MITE DETECTION AND SAMPLING.mp4"
CAMERA_INDEX = 0
FRAME_SKIP = 25
CONFIDENCE_THRESHOLD = 0.25
BEE_PADDING = 150
NUM_RECENT_FRAMES_TO_KEEP = 10   # <=== You can control how many frames to keep

# === LOAD MODELS ===
print("📦 Loading YOLO models...")
bee_model = YOLO(str(MODEL_BEE_PATH))
mite_model = YOLO(str(MODEL_VARROA_PATH))
box_annotator = sv.BoxAnnotator()

print(f'✅ Bee model loaded: {MODEL_BEE_PATH.name}')
print(f'✅ Varroa model loaded: {MODEL_VARROA_PATH.name}')

# === CAMERA / VIDEO SETUP ===
USE_CAMERA = not args.demo
USE_PICAMERA = args.picamera

if USE_PICAMERA:
    print("📷 Running with PiCamera2...")
    from picamera2 import Picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
    picam2.start()
elif USE_CAMERA:
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

if not USE_PICAMERA:
    if cap.isOpened(): 
        print(f'✅ Video opened: {DEMO_VIDEO_PATH if not USE_CAMERA else "Camera feed"}')
    else:
        print(f'❌ Failed to open video or camera.')

while True:
    # Capture frame
    if USE_PICAMERA:
        frame = picam2.capture_array()
        ret = True
    else:
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

    frame_has_mites = False  # <=== Track whether this frame has mites on any bee

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
                frame_has_mites = True   # <=== Set flag if any mite detected
                print(f"🛑 MITE DETECTED in frame {frame_count}: bee crop [{x1p}:{x2p}, {y1p}:{y2p}] conf {mconf:.2f}")

        # === SAFE HANDLING for empty detections ===
        xyxy_array = np.array(mite_boxes, dtype=np.float32)
        if xyxy_array.shape[0] == 0:
            xyxy_array = np.empty((0, 4), dtype=np.float32)

        detections_sv = sv.Detections(
            xyxy=xyxy_array,
            class_id=np.zeros(len(mite_boxes), dtype=int),
            confidence=np.array(mite_confs, dtype=np.float32),
        )

        # Annotate bee crop
        bee_crop_annotated = box_annotator.annotate(
            bee_crop.copy(), detections=detections_sv
        )

        # Manual label drawing
        for i, box in enumerate(mite_boxes):
            x1, y1, x2, y2 = map(int, box)
            label = f"{mite_labels[i]} ({mite_confs[i]:.2f})"
            cv2.putText(bee_crop_annotated, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Put crop back into frame
        frame[y1p:y2p, x1p:x2p] = bee_crop_annotated
        cv2.imshow("Bee + Varroa Detector", frame)


    # === Keep only frames that have mites ===
    if frame_has_mites:
        print(f"📸 Saving frame {frame_count} with mites")
        recent_frames = (recent_frames + [frame.copy()])[-NUM_RECENT_FRAMES_TO_KEEP:]

    # Annotate full frame with bee boxes
    frame_annotated = box_annotator.annotate(frame.copy(), detections=detections_bees_sv)

    # Show annotated frame
    cv2.imshow("🐝 Bee + Varroa Detector", frame_annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting.")
        break

# Cleanup
if not USE_PICAMERA:
    cap.release()
else:
    picam2.stop()

cv2.destroyAllWindows()

# === OPTIONAL: Plot last N frames ===
if len(recent_frames) > 0:
    print(f"\n🖼️ Displaying last {len(recent_frames)} frames with mites...")
    cols = min(len(recent_frames), 6)
    rows = (len(recent_frames) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(18, 6 * rows))
    axes = axes.flatten() if isinstance(axes, np.ndarray) else [axes]

    for idx, img in enumerate(recent_frames):
        axes[idx].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axes[idx].axis('off')

    for j in range(len(recent_frames), len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()
