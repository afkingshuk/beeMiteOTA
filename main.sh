#!/bin/bash

# Request sudo upfront
if [ "$EUID" -ne 0 ]; then
    echo "Requesting sudo permissions..."
    sudo -v || { echo "Sudo permission denied. Exiting."; exit 1; }
    # Keep-alive sudo
    while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
fi

REPO_DIR="$HOME/beeMite"
INSTALL_FLAG_FILE="$HOME/.beemite_installed"
REQ_FILE="$REPO_DIR/requirements.txt"

echo "🔍 Starting BeeMite setup..."

if [ ! -f "$INSTALL_FLAG_FILE" ]; then
    echo "System not set up yet. Installing dependencies and downloading code..."
    bash ./install_dependencies.sh || { echo "Dependency installation failed"; exit 1; }
    bash ./download_code.sh || { echo "Code download/update failed"; exit 1; }
    touch "$INSTALL_FLAG_FILE"
    echo "Installation complete."

    # Setup systemd user service
    SERVICE_FILE="$HOME/.config/systemd/user/beemite.service"
    mkdir -p "$(dirname "$SERVICE_FILE")"
    cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=BeeMite Detection Service
After=network.target

[Service]
Type=simple
ExecStart=$HOME/beeMite/run_detection.sh
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOL

    echo "Enabling user systemd service..."
    systemctl --user daemon-reload
    systemctl --user enable beemite.service
    systemctl --user start beemite.service
    echo "Service setup complete. It will start automatically on login."
else
    echo "System already set up."
fi

# === PACKAGE CHECK & AUTO-INSTALL ===
echo "🔍 Checking and installing required Python packages..."

if [ ! -f "$REQ_FILE" ]; then
    echo "⚠️ requirements.txt not found. Skipping package check."
else
    while read -r line || [[ -n "$line" ]]; do
        # Skip comments or blank lines
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue

        PACKAGE_NAME=$(echo "$line" | cut -d'=' -f1 | tr -d ' ')

        # Smart import name handling
        IMPORT_NAME=$(echo "$PACKAGE_NAME" | tr '-' '_' )

        # Manual override for known exceptions
        case "$PACKAGE_NAME" in
            "opencv-python-headless") IMPORT_NAME="cv2" ;;
            "Pillow") IMPORT_NAME="PIL" ;;
            "scikit-learn") IMPORT_NAME="sklearn" ;;
            "PyYAML") IMPORT_NAME="yaml" ;;
            "python-dateutil") IMPORT_NAME="dateutil" ;;
        esac

        # Generate small Python script to test import
        TEST_SCRIPT="
try:
    import $IMPORT_NAME
    print('✅ PACKAGE OK: $PACKAGE_NAME')
except ImportError:
    print('❌ MISSING PACKAGE: $PACKAGE_NAME')
    raise
"
        if ! python3 -c "$TEST_SCRIPT" > /dev/null 2>&1; then
            echo "➡️ Installing missing package: $PACKAGE_NAME..."
            pip install "$PACKAGE_NAME" || echo "⚠️ Failed to install $PACKAGE_NAME. Please check manually."
        fi

    done < "$REQ_FILE"
fi

# === RUN DETECTION SCRIPT ===
echo "🚦 Running detection script..."
bash ./run_detection.sh

echo "✅ Main setup complete."
exit 0
