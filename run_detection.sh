#!/bin/bash

ENV_NAME="beemite_env"
REPO_DIR="$HOME/beeMite"
PYTHON_SCRIPT="varroaDetector.py"

# Activate conda environment
echo "🟢 Activating conda environment: $ENV_NAME..."
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
conda activate $ENV_NAME

# Check camera availability
CAMERA_AVAILABLE=0
PICAMERA2_AVAILABLE=0

# Check if v4l2-ctl is available (for USB cam or Pi cam in v4l2 mode)
if command -v v4l2-ctl &>/dev/null; then
    if v4l2-ctl --list-devices | grep -q "video"; then
        CAMERA_AVAILABLE=1
    fi
else
    echo "⚠️ v4l2-ctl not found. Installing..."
    sudo apt install -y v4l-utils
    if v4l2-ctl --list-devices | grep -q "video"; then
        CAMERA_AVAILABLE=1
    fi
fi

# Check if python3-picamera2 is available
# python3 -c "import picamera2" 2>/dev/null && PICAMERA2_AVAILABLE=1

echo "🔍 CAMERA_AVAILABLE=$CAMERA_AVAILABLE, PICAMERA2_AVAILABLE=$PICAMERA2_AVAILABLE"

# Run detection based on availability
if [[ $PICAMERA2_AVAILABLE -eq 1 && $CAMERA_AVAILABLE -eq 1 ]]; then
    echo "🚀 Running with PiCamera2..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" --picamera || echo "❌ ERROR running with PiCamera2."
elif [[ $CAMERA_AVAILABLE -eq 1 ]]; then
    echo "🚀 Running with standard camera (cv2)..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" || echo "❌ ERROR running with standard camera."
else
    echo "⚠️ No camera detected. Running in DEMO mode..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" --demo || echo "❌ ERROR running in DEMO mode."
fi

echo "✅ run_detection.sh complete."
exit 0
