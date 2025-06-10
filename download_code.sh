#!/bin/bash

REPO_URL="https://github.com/afkingshuk/beeMiteOTA.git"
REPO_DIR="$HOME/beeMite"

if [ ! -d "$REPO_DIR" ]; then
    echo "📂 Cloning repo..."
    git clone "$REPO_URL" "$REPO_DIR"
else
    echo "📂 Updating repo..."
    cd "$REPO_DIR"
    git pull origin main || echo "⚠️ Git pull failed, continuing..."
fi

echo "✅ Code ready at $REPO_DIR"
exit 0
