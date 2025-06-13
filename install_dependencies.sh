#!/bin/bash
set -e

echo "📦 Installing system dependencies (USB camera version)..."

# SYSTEM PACKAGES FIRST (no Picamera2 needed)
sudo apt update
sudo apt install -y \
    libjpeg-dev libtiff-dev libpng-dev \
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
    eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
fi

# SETUP ENVIRONMENT
echo "🐍 Setting up beemite_env conda environment..."

# Remove existing env if present
if conda env list | grep -q beemite_env; then
    echo "🗑️ Removing existing beemite_env..."
    conda remove -n beemite_env --all -y
else
    echo "ℹ️ Conda env beemite_env does not exist, skipping removal."
fi

# Create new env
conda create -n beemite_env python=3.10 -y

# Activate env
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
conda activate beemite_env

# Install required pip packages
echo "📦 Installing Python packages in beemite_env from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ beemite_env setup complete."
echo "✅ install_dependencies.sh complete."
