#!/bin/bash
set -e

echo "🐝 Starting beeMite FULL SYSTEM install (no venv)..."

# 1️⃣ Update APT
echo "📦 Updating APT..."
sudo apt update
sudo apt upgrade -y

# 2️⃣ Install system packages
echo "📦 Installing system packages required..."

sudo apt install -y \
    python3 python3-pip \
    python3-libcamera libcamera-apps libcamera-dev \
    python3-prctl libcap-dev \
    python3-kms++ python3-pyqt6 \
    libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils \
    build-essential git \
    python3-opencv \
    python3-picamera2

# 3️⃣ Install Python packages (global system python3)
echo "📦 Installing Python packages globally via pip..."

# Safe versions:
sudo python3 -m pip install --upgrade pip

# Safe versions of required packages:
sudo python3 -m pip install \
    torch==2.1.2 \
    ultralytics==8.2.19 \
    supervision==0.18.0 \
    opencv-python-headless==4.9.0.80 \
    matplotlib==3.8.4 \
    numpy<2

# 4️⃣ Final message
echo "✅ beeMite SYSTEM install complete (no venv)."
echo "👉 You can now run: python3 test_picamera2_preview.py"
