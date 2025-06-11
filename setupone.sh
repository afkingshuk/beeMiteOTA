#!/bin/bash
set -e

echo "🐝 Starting global beeMite environment installation..."

# 1️⃣ Update APT
echo "📦 Updating APT..."
sudo apt update
sudo apt upgrade -y

# 2️⃣ Install system dependencies
echo "📦 Installing required system packages..."

sudo apt install -y \
    python3 python3-pip python3-venv \
    python3-libcamera libcamera-apps libcamera-dev \
    python3-prctl libcap-dev \
    python3-kms++ python3-pyqt6 \
    libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils \
    build-essential git \
    python3-opencv \
    python3-picamera2

# 3️⃣ Optional: clean old venv
echo "🗑️ Removing old venv if exists..."
rm -rf beemite_venv

# 4️⃣ Create venv with system-site-packages
echo "🐍 Creating new venv (with system-site-packages)..."
python3 -m venv beemite_venv --system-site-packages

# 5️⃣ Activate venv
source beemite_venv/bin/activate

# 6️⃣ Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 7️⃣ Install Python packages (safe versions)
echo "📦 Installing Python packages from requirements.txt..."

# Prepare a clean safe requirements.txt if needed
cat <<EOF > requirements.txt
torch==2.1.2
ultralytics==8.2.19
supervision==0.18.0
opencv-python-headless==4.9.0.80
matplotlib==3.8.4
numpy<2
EOF

# Install
pip install -r requirements.txt

# 8️⃣ Force reinstall Picamera2 to ensure pip version matches system
echo "📦 Ensuring latest Picamera2 is installed..."
pip install --force-reinstall picamera2

# 9️⃣ Done
echo "✅ Global beeMite environment installation complete."
echo "👉 To activate venv: source beemite_venv/bin/activate"
echo "👉 To run varroaDetector.py: python varroaDetector.py --picamera"
