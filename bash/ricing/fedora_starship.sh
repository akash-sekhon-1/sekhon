#!/bin/bash
set -e

# Fix GNOME Tweaks
sudo dnf install -y gnome-tweaks

# Extensions
sudo dnf install -y gnome-extensions-app --skip-unavailable

# Starship
sudo dnf copr enable -y atim/starship
sudo dnf install -y starship

# Nerd Font
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
curl -fLO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/JetBrainsMono.zip
unzip -o JetBrainsMono.zip
rm JetBrainsMono.zip
fc-cache -fv

# Kitty
sudo dnf install -y kitty
mkdir -p ~/.config/kitty

# Papirus icons
sudo dnf install -y --skip-unavailable papirus-icon-theme fastfetch || true

# add starship init to shell rc only if not already present
grep -Fqx 'eval "$(starship init bash)"' ~/.bashrc 2>/dev/null || \
    echo 'eval "$(starship init bash)"' >> ~/.bashrc

if command -v zsh >/dev/null 2>&1; then
    grep -Fqx 'eval "$(starship init zsh)"' ~/.zshrc 2>/dev/null || \
        echo 'eval "$(starship init zsh)"' >> ~/.zshrc
fi

echo "Done. Restart terminal."
