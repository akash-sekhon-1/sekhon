

#!/usr/bin/env bash
set -euo pipefail

echo -e "\n=== Vivaldi Installer (Fedora/Ubuntu) ===\n"

###############################################################################
# Basic deps
###############################################################################
if ! command -v sudo >/dev/null 2>&1; then
  echo "❌ sudo not found."
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "❌ curl not found."
  exit 1
fi

###############################################################################
# Detect distro
###############################################################################
if command -v dnf >/dev/null 2>&1; then
  DISTRO="fedora"
elif command -v apt-get >/dev/null 2>&1; then
  DISTRO="ubuntu"
else
  echo "❌ Unsupported system: only Fedora and Ubuntu/Debian."
  exit 1
fi

echo "→ Detected: $DISTRO"

###############################################################################
# Fedora branch
###############################################################################
if [[ "$DISTRO" == "fedora" ]]; then
  VIV_REPO="/etc/yum.repos.d/vivaldi.repo"
  sudo curl -fsSL https://repo.vivaldi.com/archive/vivaldi-fedora.repo \
    -o "$VIV_REPO"

  sudo rpm --import https://repo.vivaldi.com/archive/linux_signing_key.pub
  sudo dnf -y makecache
  sudo dnf -y install vivaldi-stable

  echo "✔ Vivaldi installed."
  exit 0
fi

###############################################################################
# Ubuntu/Debian branch
###############################################################################
# ensure gpg
if ! command -v gpg >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y gnupg
fi

VIV_KEYRING="/usr/share/keyrings/vivaldi-browser.gpg"
if [[ ! -f "$VIV_KEYRING" ]]; then
  curl -fsSL https://repo.vivaldi.com/archive/linux_signing_key.pub \
    | gpg --dearmor | sudo tee "$VIV_KEYRING" >/dev/null
fi

VIV_LIST="/etc/apt/sources.list.d/vivaldi.list"
sudo tee "$VIV_LIST" >/dev/null <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=$VIV_KEYRING] https://repo.vivaldi.com/archive/deb/ stable main
EOF

sudo apt-get update -y
sudo apt-get install -y vivaldi-stable

echo "✔ Vivaldi installed."
exit 0

