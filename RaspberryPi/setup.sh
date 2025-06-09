#!/bin/bash

# === CONFIGURATION ===
ENV_NAME="bee-env"
PYTHON_FILE="varroaDetector.py"
INSTALL_DIR="$HOME/miniforge3"
ENV_YML_FILE="bee_env.yml"

echo "🚀 Starting setup..."

# === UPDATE & INSTALL SYSTEM DEPS ===
sudo apt update -y
sudo apt install -y wget git libatlas-base-dev libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libgtk-3-dev libcanberra-gtk* python3-dev python3-pip cmake build-essential

# === INSTALL MINIFORGE (LIGHTWEIGHT ANACONDA FOR RASPBERRY PI) ===
if [ ! -d "$INSTALL_DIR" ]; then
    echo "📦 Installing Miniforge..."
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O ~/miniforge.sh
    bash ~/miniforge.sh -b -p $INSTALL_DIR
    echo 'export PATH="$HOME/miniforge3/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/miniforge3/bin:$PATH"
    source ~/.bashrc
else
    echo "✅ Miniforge already installed."
fi

# === INIT CONDA & CREATE ENV ===
eval "$($INSTALL_DIR/bin/conda shell.bash hook)"
conda init
source ~/.bashrc

if conda info --envs | grep -q "$ENV_NAME"; then
    echo "✅ Conda env '$ENV_NAME' already exists."
else
    echo "🧪 Creating conda environment..."
    conda create -y -n $ENV_NAME python=3.10
fi

conda activate $ENV_NAME

# === INSTALL PYTHON PACKAGES ===
echo "📦 Installing Python packages in $ENV_NAME..."

pip install --upgrade pip
pip install ultralytics supervision opencv-python numpy matplotlib roboflow picamera2

# === RUN PYTHON DETECTION SCRIPT ===
if [ -f "$PYTHON_FILE" ]; then
    echo "🎬 Running detection script: $PYTHON_FILE"
    python $PYTHON_FILE
else
    echo "❌ ERROR: Python script '$PYTHON_FILE' not found!"
    exit 1
fi
