#!/bin/bash
set -e

echo "Installing system dependencies..."

sudo apt update -y && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential cmake pkg-config libjpeg-dev libtiff-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev python3-pip libffi-dev libssl-dev libpq-dev v4l-utils

# Miniforge install if needed
if ! command -v conda &>/dev/null; then
    echo "Installing Miniforge..."
    cd /tmp
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh -O Miniforge3.sh
    bash Miniforge3.sh -b -p $HOME/miniforge3
    eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
    conda init
    echo "Miniforge installed"
else
    echo "Conda already installed"
fi

# Reload shell for conda
source ~/.bashrc || true

ENV_NAME="beemite_env"

if conda info --envs | grep -q $ENV_NAME; then
    echo "Conda environment $ENV_NAME already exists. Updating packages..."
    conda activate $ENV_NAME
    conda update -y --all
else
    conda create -y -n $ENV_NAME python=3.10
    conda activate $ENV_NAME
fi

echo "Installing python packages..."

pip install --upgrade pip setuptools wheel
if [ -f "$HOME/beeMite/requirements.txt" ]; then
    pip install -r $HOME/beeMite/requirements.txt
else
    echo "requirements.txt not found, installing packages individually"
    pip install ultralytics opencv-python-headless supervision matplotlib roboflow numpy
fi

echo "Dependencies installed."
exit 0
