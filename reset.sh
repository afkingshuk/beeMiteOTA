#!/bin/bash
# reset_conda_envs.sh
# Deletes all Conda envs except base, clears cache, then runs main install script

set -e  # Exit if any command fails

# === CONFIG ===
# Path to your main install script:
MAIN_INSTALL_SCRIPT="main.sh"   # <== change this to your script path!

# Optional: path to Conda (uncomment if needed)
# export PATH="$HOME/miniconda3/bin:$PATH"

echo "==== Listing current Conda environments ===="
conda env list

# === Deleting all Conda envs except base ===
echo "==== Deleting Conda environments (except base) ===="

for env in $(conda env list | awk '{print $1}' | grep -v "#" | grep -v "base"); do
    echo "Removing env: $env"
    conda env remove --name "$env" -y
done

# === Optional: Clear Conda package cache ===
echo "==== Clearing Conda package cache ===="
conda clean --all -y

# === Optional: Force delete envs folder (if needed, uncomment) ===
# echo "==== Force deleting envs folder ===="
# rm -rf ~/miniconda3/envs/*
# or: rm -rf ~/anaconda3/envs/*

# === Final check ===
echo "==== Remaining Conda environments ===="
conda env list

# === Running main install script ===
if [ -f "$MAIN_INSTALL_SCRIPT" ]; then
    echo "==== Running main install script: $MAIN_INSTALL_SCRIPT ===="
    bash "$MAIN_INSTALL_SCRIPT"
else
    echo "ERROR: Main install script not found: $MAIN_INSTALL_SCRIPT"
    exit 1
fi

echo "==== Done. System reset and reinstall completed. ===="
