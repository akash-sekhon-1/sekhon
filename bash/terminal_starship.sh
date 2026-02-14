#!/bin/bash
set -e

# Fix GNOME Tweaks
sudo dnf install -y gnome-tweaks

# Extensions 
sudo dnf install -y gnome-extensions-app --skip-unavailable

# Starship
sudo dnf copr enable -y atim/starship
sudo dnf install -y starship
echo 'eval "$(starship init bash)"' >> ~/.bashrc

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
cat > ~/.config/kitty/kitty.conf << 'EOF'
font_family      JetBrainsMono Nerd Font
font_size        11.0
EOF

# Papirus icons
sudo dnf install -y papirus-icon-theme

echo "Done. Restart terminal and enable extensions at https://extensions.gnome.org"