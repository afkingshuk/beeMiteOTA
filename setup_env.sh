#!/bin/bash
set -e

echo "🐍 Setting up beemite_env conda environment..."

# Remove existing env if present
conda remove -n beemite_env --all -y || true

# Create new env
conda create -n beemite_env python=3.10 -y

# Activate env
eval "$(conda shell.bash hook)"
conda activate beemite_env

# Install required pip packages
echo "📦 Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Force reinstall Picamera2 (links to system libcamera)
echo "📦 Installing Picamera2..."
pip install --force-reinstall picamera2

echo "✅ beemite_env setup complete."
