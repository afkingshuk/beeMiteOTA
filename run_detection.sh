#!/bin/bash

ENV_NAME="beemite_env"
REPO_DIR="$HOME/beeMite"
PYTHON_SCRIPT="RaspberryPi/varroaDetector.py"

eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
conda activate $ENV_NAME

echo "Checking for camera..."

CAMERA_AVAILABLE=0

if command -v v4l2-ctl &>/dev/null; then
    if v4l2-ctl --list-devices | grep -q "video"; then
        CAMERA_AVAILABLE=1
    fi
else
    echo "v4l2-ctl not found, installing..."
    sudo apt install -y v4l-utils
    if v4l2-ctl --list-devices | grep -q "video"; then
        CAMERA_AVAILABLE=1
    fi
fi

if [ $CAMERA_AVAILABLE -eq 1 ]; then
    echo "Camera found, starting detection..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT"
else
    echo "No camera detected. Starting demo mode..."
    python3 "$REPO_DIR/$PYTHON_SCRIPT" --demo
fi

exit 0
