#!/usr/bin/env bash
set -euo pipefail

echo -e "\n=== Microsoft Edge Installer (Fedora/Ubuntu) ===\n"

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
  EDGE_REPO="/etc/yum.repos.d/microsoft-edge.repo"
  sudo tee "$EDGE_REPO" >/dev/null <<'EOF'
[microsoft-edge]
name=Microsoft Edge
baseurl=https://packages.microsoft.com/yumrepos/edge
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

  sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
  sudo dnf -y makecache
  sudo dnf -y install microsoft-edge-stable

  echo "✔ Edge installed."
  exit 0
fi

###############################################################################
# Ubuntu/Debian branch
###############################################################################
MS_KEYRING="/usr/share/keyrings/microsoft-edge.gpg"
if [[ ! -f "$MS_KEYRING" ]]; then
  curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor | sudo tee "$MS_KEYRING" >/dev/null
fi

EDGE_LIST="/etc/apt/sources.list.d/microsoft-edge.list"
sudo tee "$EDGE_LIST" >/dev/null <<EOF
deb [arch=$(dpkg --print-architecture) signed-by=$MS_KEYRING] https://packages.microsoft.com/repos/edge stable main
EOF

sudo apt-get update -y
sudo apt-get install -y microsoft-edge-stable

echo "✔ Edge installed"
exit 0

