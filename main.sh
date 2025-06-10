#!/bin/bash

# Request sudo upfront
if [ "$EUID" -ne 0 ]; then
    echo "Requesting sudo permissions..."
    sudo -v || { echo "Sudo permission denied. Exiting."; exit 1; }
    # Keep-alive: update existing sudo time stamp until script finishes
    while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &
fi

REPO_URL="https://github.com/afkingshuk/beeMite.git"
INSTALL_FLAG_FILE="$HOME/.beemite_installed"
REPO_DIR="$HOME/beeMite"

echo "Starting BeeMite setup..."

if [ ! -f "$INSTALL_FLAG_FILE" ]; then
    echo "System not set up yet. Installing dependencies and downloading code..."
    bash ./install_dependencies.sh || { echo "Dependency installation failed"; exit 1; }
    bash ./download_code.sh || { echo "Code download/update failed"; exit 1; }
    touch "$INSTALL_FLAG_FILE"
    echo "Installation complete."

    # Setup systemd user service for auto start
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

echo "Starting detection script..."
bash ./run_detection.sh

exit 0
