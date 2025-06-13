#!/bin/bash
set -e

echo "📦 Installing system dependencies..."

# SYSTEM PACKAGES FIRST (includes libcamera stack + Picamera2 deps + GPIO for DHT22)
sudo apt update
sudo apt install -y \
    python3-libcamera libcamera-apps libcamera-dev python3-prctl libcap-dev \
    python3-kms++ python3-pyqt6 \
    libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils \
    build-essential python3-pip git \
    python3-libgpiod  # for DHT22 GPIO access

# INSTALL MINIFORGE (if not installed)
if ! command -v conda &> /dev/null; then
    echo "📥 Installing Miniforge..."
    cd /tmp
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O Miniforge3.sh
    bash Miniforge3.sh -b -p $HOME/miniforge3
    eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
    conda init
    echo "✅ Miniforge installed."
    source ~/.bashrc
else
    echo "✅ Conda already installed."
    eval "$(conda shell.bash hook)"
fi

# Setup beemite_env conda environment
echo "🐍 Setting up beemite_env conda environment..."

# Remove existing env if present
conda remove -n beemite_env --all -y || true

# Create new env
conda create -n beemite_env python=3.10 -y

# Activate env
eval "$(conda shell.bash hook)"
conda activate beemite_env

# Install required pip packages
echo "📦 Installing Python packages in beemite_env..."
pip install --upgrade pip
pip install numpy matplotlib ultralytics supervision opencv-python-headless torch Adafruit_DHT

echo "✅ beemite_env setup complete."
echo "✅ install_dependencies.sh complete."
