#!/usr/bin/env python3

import os
import subprocess
import sys
import venv
import shutil

# === CONFIGURATION ===
REQUIRED_SYSTEM_PACKAGES = [
    'python3-libcamera',
    'libcamera-apps',
    'libcamera-dev',
    'python3-prctl',
    'libcap-dev',
    'python3-kms++',
    'python3-pyqt6',
    'libjpeg-dev',
    'libtiff-dev',
    'libpng-dev',
    'libavcodec-dev',
    'libavformat-dev',
    'libswscale-dev',
    'libv4l-dev',
    'v4l-utils',
    'build-essential',
    'python3-pip',
    'git'
]

VENV_DIR = './beemite_env'
PYTHON_BIN = f'{VENV_DIR}/bin/python'
PIP_BIN = f'{VENV_DIR}/bin/pip'

# === FUNCTIONS ===

def run_command(cmd, sudo=False):
    if sudo:
        cmd = ['sudo'] + cmd
    print(f"👉 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def check_system_package(pkg_name):
    result = subprocess.run(['dpkg', '-l', pkg_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def install_system_packages():
    print("📦 Checking system packages...")
    for pkg in REQUIRED_SYSTEM_PACKAGES:
        if check_system_package(pkg):
            print(f"✅ {pkg} already installed.")
        else:
            print(f"❌ {pkg} missing — installing...")
            run_command(['apt', 'install', '-y', pkg], sudo=True)

def create_venv():
    if os.path.exists(VENV_DIR):
        print("🗑️ Removing existing venv...")
        shutil.rmtree(VENV_DIR)

    print("🐍 Creating new venv...")
    builder = venv.EnvBuilder(with_pip=True, system_site_packages=True)
    builder.create(VENV_DIR)
    print("✅ venv created at", VENV_DIR)

def install_pip_packages():
    print("📦 Installing pip packages from requirements.txt...")
    run_command([PIP_BIN, 'install', '--upgrade', 'pip'])

    # Install your requirements.txt
    run_command([PIP_BIN, 'install', '-r', 'requirements.txt'])

    # Force-reinstall Picamera2
    print("📦 Installing Picamera2...")
    run_command([PIP_BIN, 'install', '--force-reinstall', 'picamera2'])

def run_varroa_detector():
    print("🚀 Running varroaDetector.py inside venv...")
    run_command([PYTHON_BIN, 'varroaDetector.py'])

# === MAIN ===

if __name__ == '__main__':
    print("🐝 Starting beeMite_installer.py...")

    try:
        # 1️⃣ System packages
        install_system_packages()

        # 2️⃣ Venv
        create_venv()

        # 3️⃣ Pip packages
        install_pip_packages()

        # 4️⃣ Run main detector
        run_varroa_detector()

        print("✅ beeMite installation and run complete!")

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR during command: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("👋 Interrupted by user.")
        sys.exit(1)
