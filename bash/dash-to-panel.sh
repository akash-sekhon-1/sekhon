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
# Install Dash-to-Panel
# -------------------------------------
DTP_UUID="dash-to-panel@jderose9.github.com"
DTP_URL="https://extensions.gnome.org/extension-data/dash-to-paneljderose9.github.com.v66.shell-extension.zip"

if gnome-extensions list | grep -q "$DTP_UUID"; then
    echo "[INFO] Dash-to-Panel already installed."
else
    echo "[INFO] Installing Dash-to-Panel..."
    TMP_ZIP2="$(mktemp)"
    curl -fsSL "$DTP_URL" -o "$TMP_ZIP2"
    gnome-extensions install --force "$TMP_ZIP2"
    rm -f "$TMP_ZIP2"
fi

# -------------------------------------
# Enable Extension
# -------------------------------------
echo "[INFO] Enabling Dash-to-Panel..."
gnome-extensions enable "$DTP_UUID" 2>/dev/null || true

echo "[INFO] Dash-to-Panel installation complete."
echo "[INFO] Restart GNOME Shell (logout/login or Alt+F2 → r) to apply fully"
