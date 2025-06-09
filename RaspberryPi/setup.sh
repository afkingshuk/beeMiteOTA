#!/bin/bash

set -e

echo "🚀 Starting unattended setup for Bee Varroa Detection on Raspberry Pi..."

# === CONFIGURATION ===
ENV_NAME="beemite_env"
PYTHON_VERSION="3.10"
SCRIPT_NAME="varroaDetector.py"
ANACONDA_INSTALLER="Anaconda3-2023.07-2-Linux-aarch64.sh"
ANACONDA_URL="https://repo.anaconda.com/archive/$ANACONDA_INSTALLER"

# === 1. Install System Dependencies ===
echo "🔧 Installing required system packages..."
sudo apt update && sudo apt install -y \
  libcap-dev \
  python3-opencv \
  libatlas-base-dev \
  libjpeg-dev \
  libtiff-dev \
  libpng-dev \
  libavcodec-dev \
  libavformat-dev \
  libswscale-dev \
  libv4l-dev \
  libxvidcore-dev \
  libx264-dev \
  libgtk-3-dev \
  libcanberra-gtk* \
  cmake \
  unzip \
  wget \
  git \
  curl \
  build-essential

# === 2. Install Anaconda if not already installed ===
if ! command -v conda &> /dev/null; then
  echo "📦 Installing Anaconda..."
  wget -O ~/Downloads/$ANACONDA_INSTALLER "$ANACONDA_URL"
  bash ~/Downloads/$ANACONDA_INSTALLER -b -p $HOME/anaconda3
  eval "$($HOME/anaconda3/bin/conda shell.bash hook)"
  conda init
else
  echo "✅ Anaconda already installed."
  eval "$(conda shell.bash hook)"
fi

# === 3. Create and activate conda environment ===
if ! conda info --envs | grep -q "$ENV_NAME"; then
  echo "🐍 Creating conda environment $ENV_NAME with Python $PYTHON_VERSION..."
  conda create -y -n $ENV_NAME python=$PYTHON_VERSION
else
  echo "✅ Conda environment $ENV_NAME already exists."
fi

echo "🔄 Activating conda environment..."
conda activate $ENV_NAME

# === 4. Install Python packages ===
echo "📦 Installing required Python packages in environment..."
pip install --upgrade pip
pip install opencv-python
pip install roboflow
pip install supervision
pip install matplotlib
pip install numpy
pip install ultralytics
pip install picamera2

# === 5. Run your Python detection script ===
echo "🎬 Running detection script: $SCRIPT_NAME"
python $SCRIPT_NAME
