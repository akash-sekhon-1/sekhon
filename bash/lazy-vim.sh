



#!/bin/bash
set -euo pipefail

printf "\nWelcome to Fedora Lazy VIM install\n"
logs="$HOME/.local/sekhon/logs.txt"

# 1. Install lazy vim
sudo dnf update -y
sudo dnf install -y neovim
sudo dnf install -y --skip-unavailable git ripgrep fd-find 2> $logs

DT=$(date +"%Y-%m-%d_%H-%M-%S")

if [[ -d ~/.config/nvim ]]; then
    mkdir -p ~/.config/nvim_bak
    mv ~/.config/nvim ~/.config/nvim_bak/nvim_bak_$DT
fi

mkdir -p ~/.config/nvim
git clone https://github.com/LazyVim/starter ~/.config/nvim

rm -rf ~/.config/nvim/.git


# 2. Download the Fonts (for rendering icons and all)
TMP_DIR=/tmp/sekhon_jetbrains 
if [[ -d $TMP_DIR ]]; then
    rm -rf $TMP_DIR
fi

mkdir -p $TMP_DIR $TMP_DIR/dispatch
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/JetbrainsMono.zip -O $TMP_DIR/jetbrainsmono.zip
unzip $TMP_DIR/jetbrainsmono.zip -d $TMP_DIR/dispatch

cp --force $TMP_DIR/dispatch/*.ttf ~/.local/share/fonts/
fc-cache -fv



# 3. Set the default fonts to nerd fonts

mkdir -p ~/.config/fontconfig/conf.d
cat > ~/.config/fontconfig/conf.d/99-nerdfont-priority.conf <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
    <alias>
        <family>monospace</family>
        <prefer>
            <family>JetBrainsMono Nerd Font</family>
            <family>JetBrainsMono NFM</family>
        </prefer>
    </alias>
</fontconfig>
EOF

fc-cache -fv











