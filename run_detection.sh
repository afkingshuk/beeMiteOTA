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

# Check if v4l2-ctl is available (for USB camera detection)
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

echo "🔍 CAMERA_AVAILABLE=$CAMERA_AVAILABLE"

# Run detection based on availability
if [[ $CAMERA_AVAILABLE -eq 1 ]]; then
    echo "🚀 Running with USB camera (cv2)..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" || echo "❌ ERROR running with USB camera."
else
    echo "⚠️ No USB camera detected. Running in DEMO mode..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" --demo || echo "❌ ERROR running in DEMO mode."
fi

echo "✅ run_detection.sh complete."
exit 0
