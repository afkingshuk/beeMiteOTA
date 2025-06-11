#!/bin/bash
set -e

echo "📦 Installing system dependencies..."

# SYSTEM PACKAGES FIRST (libcamera stack + Picamera2 deps)
sudo apt update
sudo apt install -y \
    libcamera-dev libcamera-apps python3-libcamera python3-kms++ python3-pyqt6 \
    libcap-dev python3-prctl libatlas-base-dev libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils \
    build-essential python3-pip git

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

# SETUP beemite_env conda environment
./setup_env.sh

echo "✅ install_dependencies.sh complete."
