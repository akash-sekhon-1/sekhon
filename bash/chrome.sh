#!/usr/bin/env bash
set -euo pipefail

echo -e "\n=== Google Chrome Installer (Fedora/Ubuntu) ===\n"

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
  CHROME_REPO="/etc/yum.repos.d/google-chrome.repo"
  sudo tee "$CHROME_REPO" >/dev/null <<'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF

  sudo rpm --import https://dl.google.com/linux/linux_signing_key.pub
  sudo dnf -y makecache
  sudo dnf -y install google-chrome-stable

  echo "✔ Chrome installed."
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

GC_KEYRING="/usr/share/keyrings/google-chrome.gpg"
if [[ ! -f "$GC_KEYRING" ]]; then
  curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor | sudo tee "$GC_KEYRING" >/dev/null
fi

GC_LIST="/etc/apt/sources.list.d/google-chrome.list"
sudo tee "$GC_LIST" >/dev/null <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=$GC_KEYRING] http://dl.google.com/linux/chrome/deb/ stable main
EOF

sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

echo "✔ Chrome installed."
exit 0

