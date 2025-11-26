
#!/bin/bash

# -------- Platform detection and lightweight utilities ------------

# FEDORA
if command -v dnf >/dev/null 2>&1; then
    echo "You are using dnf based platform"
    sudo dnf upgrade -y || true

    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip fd-find ripgrep; do
        sudo dnf install -y "$pkg" || echo "failed: $pkg"
    done


# TERMUX
elif command -v pkg >/dev/null 2>&1; then
    echo "You are using Termux"
    pkg update -y || true
    pkg upgrade -y || true

    # Termux equivalents
    for pkg in xclip vim neovim htop tree curl wget zip unzip p7zip ripgrep fd; do
        pkg install -y "$pkg" || echo "failed: $pkg"
    done
    # gedit/tilix/terminator/gparted do not exist on Android


# ARCH
elif command -v pacman >/dev/null 2>&1; then
    echo "You are using Arch-based platform"
    sudo pacman -Syu --noconfirm || true

    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip ripgrep fd; do
        sudo pacman -S --noconfirm "$pkg" || echo "failed: $pkg"
    done


# UBUNTU
elif command -v apt-get >/dev/null 2>&1; then
    echo "You are using Ubuntu/Debian"

    sudo apt-get update -y || true
    sudo apt-get upgrade -y || true

    for pkg in xclip vim neovim gedit tilix terminator htop gparted tree curl wget zip unzip p7zip-full ripgrep fd-find; do
        sudo apt-get install -y "$pkg" || echo "failed: $pkg"
    done

fi