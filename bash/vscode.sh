#!/usr/bin/env bash
set -euo pipefail

echo -e "\n=== VS Code Installer (Universal Linux) ===\n"

###############################################################################
# 0. Dependency checks (curl + sudo)
###############################################################################

if ! command -v curl >/dev/null 2>&1; then
    echo "❌ curl is required but not installed. Install curl and rerun."
    exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
    echo "❌ sudo is required but not installed. Install sudo and rerun."
    exit 1
fi

###############################################################################
# 1. Detect Package Manager
###############################################################################

PKG=""
if   command -v dnf >/dev/null 2>&1;      then PKG="dnf"
elif command -v yum >/dev/null 2>&1;      then PKG="yum"
elif command -v apt-get >/dev/null 2>&1;  then PKG="apt"
elif command -v pacman >/dev/null 2>&1;   then PKG="pacman"
else
    echo "❌ Unsupported Linux distribution (no dnf/yum/apt/pacman found)."
    exit 1
fi

echo "→ Package manager detected: $PKG"


###############################################################################
# 2. Handle RPM-Based Distros (Fedora, RHEL, Rocky, Alma, openSUSE)
###############################################################################

if [[ "$PKG" == "dnf" || "$PKG" == "yum" ]]; then
    echo -e "\n=== RPM-Based System Detected ===\n"

    REPO_FILE="/etc/yum.repos.d/vscode.repo"

    # Create VS Code repo idempotently
    if [ ! -f "$REPO_FILE" ]; then
        sudo tee "$REPO_FILE" >/dev/null <<'EOF'
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF
    fi

    # Enforce IPv4 for Microsoft repo (valid yum/dnf per-repo opt)
    if ! grep -qF "ip_resolve=4" "$REPO_FILE"; then
        sudo sed -i '/^baseurl=/a ip_resolve=4' "$REPO_FILE"
    fi

    # Import GPG key idempotently
    if ! rpm -q gpg-pubkey --qf "%{VERSION}-%{RELEASE} %{SUMMARY}\n" | grep -qi microsoft; then
        curl -4 -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo rpm --import -
    fi

    # Download latest VS Code RPM
    TMP_DIR="/tmp/vscode_setup"
    mkdir -p "$TMP_DIR"
    RPM_FILE="$TMP_DIR/vscode.rpm"

    # Current stable RPM redirect (x64)
    RPM_URL="https://code.visualstudio.com/sha/download?build=stable&os=linux-rpm-x64"

    echo "→ Downloading VS Code (RPM)…"
    curl -4 -L --fail -o "$RPM_FILE" "$RPM_URL"

    echo "→ Installing/upgrading VS Code…"
    sudo $PKG install -y "$RPM_FILE"

    rm -f "$RPM_FILE"

    echo -e "\n✔ VS Code installed/updated successfully (RPM-based)."
    exit 0
fi


###############################################################################
# 3. Debian/Ubuntu (APT-based)
###############################################################################

if [[ "$PKG" == "apt" ]]; then
    echo -e "\n=== Debian/Ubuntu System Detected ===\n"

    # Microsoft signing key
    KEY_PATH="/usr/share/keyrings/microsoft.gpg"
    if [ ! -f "$KEY_PATH" ]; then
        curl -4 -fsSL https://packages.microsoft.com/keys/microsoft.asc \
            | gpg --dearmor | sudo tee "$KEY_PATH" >/dev/null
    fi

    # Repository
    LIST_FILE="/etc/apt/sources.list.d/vscode.list"
    if [ ! -f "$LIST_FILE" ]; then
        echo "deb [arch=$(dpkg --print-architecture) signed-by=$KEY_PATH] https://packages.microsoft.com/repos/code stable main" \
            | sudo tee "$LIST_FILE" >/dev/null
    fi

    echo "→ Updating APT metadata…"
    sudo apt-get update -y

    echo "→ Installing/upgrading VS Code…"
    sudo apt-get install -y code

    echo -e "\n✔ VS Code installed/updated successfully (APT-based)."
    exit 0
fi


###############################################################################
# 4. Arch Linux (Pacman-based)
###############################################################################

if [[ "$PKG" == "pacman" ]]; then
    echo -e "\n=== Arch Linux System Detected ===\n"

    # Install from AUR via binary if yay/pamac available
    if command -v yay >/dev/null 2>&1; then
        echo "→ Installing VS Code via yay (AUR)"
        yay -S --noconfirm visual-studio-code-bin
        echo "✔ VS Code installed/updated successfully on Arch."
        exit 0
    fi

    if command -v pamac >/dev/null 2>&1; then
        echo "→ Installing VS Code via pamac (AUR)"
        pamac install visual-studio-code-bin --no-confirm
        echo "✔ VS Code installed/updated successfully on Arch."
        exit 0
    fi

    echo "❌ No AUR helper found (yay/pamac required for VS Code)."
    exit 1
fi