#!/bin/bash

set -e  # Exit on error

echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing required system dependencies..."
sudo apt install -y \
  python3 python3-pip python3-venv python3-dev \
  libatlas-base-dev libjpeg-dev libpng-dev \
  libtiff-dev libavcodec-dev libavformat-dev libswscale-dev \
  libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev \
  libtbb-dev qtbase5-dev \
  libopenexr-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libhdf5-dev cmake build-essential git wget unzip libcamera-dev

echo "🐍 Setting up Python virtual environment..."
python3 -m venv ~/beemite_env
source ~/beemite_env/bin/activate

echo "🐍 Upgrading pip and installing Python packages..."
pip install --upgrade pip

# Install only compatible versions of required packages
pip install \
  opencv-python-headless \
  numpy \
  supervision \
  matplotlib \
  ultralytics \
  picamera2

echo "📂 Cloning your BeeMite repository (if not already cloned)..."
cd ~
if [ ! -d "beeMite" ]; then
  git clone https://github.com/afkingshuk/beeMite.git
fi

echo "🚀 Running detection script..."
cd ~/beeMite/RaspberryPi
python varroaDetector.py
