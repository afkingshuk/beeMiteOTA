#!/bin/bash

# === VARROA DETECTION SETUP SCRIPT FOR RASPBERRY PI OS (DEBIAN 12 BOOKWORM) ===
# Author: Kingshuk
# Purpose: Unattended setup for Bee + Varroa Mite detection using PiCamera2

set -e

echo "🔍 Checking for Raspberry Pi OS (Debian 12 Bookworm)..."
. /etc/os-release
if [[ "$VERSION_CODENAME" != "bookworm" ]]; then
    echo "❌ This script is intended for Raspberry Pi OS (Debian 12 Bookworm)."
    exit 1
fi

echo "✅ Detected Raspberry Pi OS Bookworm"

echo "🔁 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing core dependencies..."
sudo apt install -y python3 python3-pip python3-venv git libatlas-base-dev libhdf5-dev libhdf5-serial-dev libjpeg-dev libqtgui4 libqt4-test libilmbase-dev libopenexr-dev libgstreamer1.0-dev libavcodec-dev libavformat-dev libswscale-dev libtbb2 libtbb-dev libdc1394-22-dev

echo "🎥 Enabling camera support..."
sudo raspi-config nonint do_camera 0
echo "✅ Camera enabled (you may need to reboot)"

echo "📦 Installing libcamera + PiCamera2..."
sudo apt install -y libcamera-dev libcamera-apps python3-libcamera python3-picamera2

echo "🧪 Testing camera..."
libcamera-hello --version || echo "⚠️ libcamera test skipped or failed (headless?)"

echo "🐍 Creating Python virtual environment..."
cd ~
python3 -m venv beemite_env
source ~/beemite_env/bin/activate

echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install opencv-python numpy matplotlib supervision ultralytics

echo "✅ Python environment ready."

echo "📂 Cloning project (if not already)..."
cd ~
if [ ! -d "beeMite" ]; then
    git clone https://github.com/afkingshuk/beeMite.git
fi

echo "📁 Entering RaspberryPi project folder..."
cd ~/beeMite/RaspberryPi

echo "🚦 Running live detector..."
python3 varroaDetector.py
