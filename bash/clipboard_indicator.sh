#!/bin/bash
set -euo pipefail

# -------------------------------------
# Resolve GNOME Shell version
# -------------------------------------
GNOME_VER=$(gnome-shell --version | awk '{print $3}')
echo "[INFO] Detected GNOME Shell version: $GNOME_VER"

# -------------------------------------
# Ensure required tools exist
# -------------------------------------
if ! command -v gnome-extensions >/dev/null 2>&1 ; then
    echo "[INFO] Installing gnome-extensions tooling..."
    sudo dnf install -y gnome-shell-extension-prefs gnome-extensions-app
fi

if ! command -v unzip >/dev/null 2>&1 ; then
    echo "[INFO] Installing unzip..."
    sudo dnf install -y unzip
fi

# -------------------------------------
# Install Clipboard Indicator
# -------------------------------------
CLIP_UUID="clipboard-indicator@tudmotu.com"
CLIP_URL="https://extensions.gnome.org/extension-data/clipboard-indicatortudmotu.com.v68.shell-extension.zip"

if gnome-extensions list | grep -q "$CLIP_UUID"; then
    echo "[INFO] Clipboard Indicator already installed."
else
    echo "[INFO] Installing Clipboard Indicator..."
    TMP_ZIP="$(mktemp)"
    curl -fsSL "$CLIP_URL" -o "$TMP_ZIP"
    gnome-extensions install --force "$TMP_ZIP"
    rm -f "$TMP_ZIP"
fi

# -------------------------------------
# Enable Extension
# -------------------------------------
echo "[INFO] Enabling Clipboard Indicator..."
gnome-extensions enable "$CLIP_UUID" 2>/dev/null || true

echo "[INFO] Clipboard Indicator installation complete."
echo "[INFO] Restart GNOME Shell (logout/login or Alt+F2 → r) to apply fully."

