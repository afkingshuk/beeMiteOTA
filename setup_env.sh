#!/bin/bash
set -e

echo "🐍 Setting up beemite_env conda environment..."

# Remove existing env (optional safety — prevents broken envs)
conda remove -n beemite_env --all -y || true

# Create new env with --system-site-packages → required for Picamera2
conda create -n beemite_env --system-site-packages python=3.10 -y

# Activate env
eval "$(conda shell.bash hook)"
conda activate beemite_env

# Install required pip-only packages
echo "📦 Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Force reinstall Picamera2 to link to system libcamera bindings
echo "📦 Installing Picamera2 (force reinstall)..."
pip install --force-reinstall picamera2

echo "✅ beemite_env setup complete."
