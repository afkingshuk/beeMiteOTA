#!/bin/bash
set -e

echo "🐝 Starting USB camera beeMite installer..."

# 1️⃣ Install Miniforge if not present
if ! command -v conda &> /dev/null; then
    echo "📦 Installing Miniforge..."
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O Miniforge3.sh
    bash Miniforge3.sh -b -p $HOME/miniforge3
    eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
    conda init
    echo "✅ Miniforge installed."
else
    echo "✅ Miniforge already installed."
    eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
fi

# 2️⃣ Create testenv
echo "🐍 Creating Conda env: testenv"
conda remove -n testenv --all -y || true
conda create -n testenv python=3.10 -y
conda activate testenv

# 3️⃣ Install required Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install \
    torch==2.1.2 \
    ultralytics==8.2.19 \
    supervision==0.18.0 \
    opencv-python-headless==4.9.0.80 \
    matplotlib==3.8.4 \
    numpy<2

# 4️⃣ Run test python code
echo "🚀 Running USB camera test with detector..."
python usb_cam_detector.py

# 5️⃣ Done
echo "✅ USB camera beeMite test complete."
