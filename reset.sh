#!/bin/bash
# full_reset_conda_autodetect.sh
# Fully reset Conda / Miniforge + BeeMite system and run main setup

set -e  # Exit on error

# === Auto-detect Conda path ===
echo "==== Detecting Conda installation ===="
CONDA_BIN=$(which conda 2>/dev/null || true)

if [ -z "$CONDA_BIN" ]; then
    echo "WARNING: Conda is not installed or not in PATH."
    CONDA_DIR=""
else
    CONDA_DIR=$(dirname "$(dirname "$CONDA_BIN")")
    echo "Detected Conda directory: $CONDA_DIR"
fi

# === CONFIG: Path to your main BeeMite install script ===
MAIN_INSTALL_SCRIPT="$HOME/beeMite/main.sh"

# === Proceed to Conda removal ===
if [ -n "$CONDA_DIR" ] && [ -d "$CONDA_DIR" ]; then
    echo "==== Removing Conda directory: $CONDA_DIR ===="
    rm -rf "$CONDA_DIR"
    echo "==== Conda directory removed. ===="
else
    echo "Skipping Conda directory removal."
fi

# === Clean Conda files in home ===
echo "==== Cleaning Conda-related files in home directory ===="
rm -rf ~/.condarc ~/.conda ~/.continuum

# === Remove Conda init lines ===
echo "==== Removing Conda init lines from ~/.bashrc ===="
sed -i '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.bashrc

# === Optional: clean zshrc too ===
# sed -i '/# >>> conda initialize >>>/,/# <<< conda initialize <<</d' ~/.zshrc

# === Final check ===
echo "==== Final check: Conda command availability ===="
if command -v conda &> /dev/null; then
    echo "WARNING: Conda still available in PATH. You may need to restart shell or clean PATH manually."
else
    echo "OK: Conda command no longer available."
fi

# === Remove BeeMite install flag ===
echo "==== Removing BeeMite install flag ===="
rm -f "$HOME/.beemite_installed"

# # === Run main BeeMite install script ===
# if [ -f "$MAIN_INSTALL_SCRIPT" ]; then
#     echo "==== Running BeeMite main install script: $MAIN_INSTALL_SCRIPT ===="
#     bash "$MAIN_INSTALL_SCRIPT"
# else
#     echo "ERROR: Main BeeMite install script not found: $MAIN_INSTALL_SCRIPT"
#     exit 1
# fi

echo "==== Complete system reset and reinstall done! ===="
