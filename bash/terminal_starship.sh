

#!/bin/bash
# ================================================
# fedora-rice-setup.sh
# One-click GNOME rice for fresh Fedora 43 (2026)
# Includes: Kitty + Starship + Orchis theme + Papirus + Nerd Font + popular extensions
# Run with: bash fedora-rice-setup.sh
# ================================================

set -euo pipefail

echo "🚀 Starting full Fedora GNOME rice setup..."

# 1. Update everything
sudo dnf update -y

# 2. Install core packages
sudo dnf install -y \
    dnf-plugins-core \
    gnome-tweaks \
    kitty \
    fastfetch \
    papirus-icon-theme \
    adwaita-icon-theme \
    jetbrains-mono-fonts-all \
    chrome-gnome-shell \
    python3-pip

# 3. Install Starship (official method, always up-to-date)
curl -sS https://starship.rs/install.sh | sh -s -- -y

# 4. Install gnome-extensions-cli (gext) for easy extension management
python3 -m pip install --user --upgrade gnome-extensions-cli

# 5. Install Nerd Font (JetBrains Mono - best for Starship in 2026)
echo "📥 Installing JetBrains Mono Nerd Font..."
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
curl -fLO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/JetBrainsMono.zip
unzip -o JetBrainsMono.zip
rm JetBrainsMono.zip
fc-cache -fv

# 6. Install Orchis theme (top-rated Material Design theme for GNOME 49)
echo "🎨 Installing Orchis theme..."
mkdir -p ~/.themes
cd ~/.themes
wget -q https://github.com/vinceliuice/Orchis-theme/releases/latest/download/Orchis.tar.xz -O orchis.tar.xz
tar -xf orchis.tar.xz
rm orchis.tar.xz
mv Orchis* Orchis 2>/dev/null || true

# 7. Install Starship config (my 2026 favorite: clean, Catppuccin-inspired, right-side time, fill line)
mkdir -p ~/.config
cat > ~/.config/starship.toml << 'EOF'
# ========================================
# Starship config - Clean 2026 Aesthetic
# Catppuccin Mocha palette + powerline feel
# ========================================

format = """$os$directory$git_branch$git_status$python$nodejs$rust$fill$character"""
right_format = """$time$cmd_duration$status"""
add_newline = false

# Palette
[palettes.catppuccin_mocha]
rosewater = "#f5e0dc"
flamingo = "#f2cdcd"
pink = "#f5c2e7"
mauve = "#cba6f7"
red = "#f38ba8"
maroon = "#eba0ac"
peach = "#fab387"
yellow = "#f9e2af"
green = "#a6e3a1"
teal = "#94e2d5"
sky = "#89dceb"
sapphire = "#74c7ec"
blue = "#89b4fa"
lavender = "#b4befe"
text = "#cdd6f4"
subtext1 = "#bac2de"
subtext0 = "#a6adc8"
overlay2 = "#9399b2"
overlay1 = "#7f849c"
overlay0 = "#6c7086"
surface2 = "#585b70"
surface1 = "#45475a"
surface0 = "#313244"
base = "#1e1e2e"
mantle = "#181825"
crust = "#11111b"

# Modules
[os]
disabled = false
format = "[$symbol]($style) "
style = "bold blue"
symbols.Fedora = "󰣛 "

[directory]
truncation_length = 3
truncate_to_repo = true
style = "bold lavender"
format = "[$path]($style)[$read_only]($read_only_style) "

[git_branch]
style = "bold mauve"
format = "[$symbol$branch]($style) "

[git_status]
style = "bold red"
format = "[$all_status$ahead_behind]($style) "

[python]
style = "bold green"
format = "[$symbol$version]($style) "

[character]
success_symbol = "[❯](bold green)"
error_symbol = "[❯](bold red)"

[fill]
symbol = "─"
style = "dimmed text"

[time]
disabled = false
format = "[$time]($style) "
style = "bold dimmed text"
time_format = "%H:%M"

[cmd_duration]
format = "[$duration]($style) "
style = "bold yellow"
min_time = 2000

[status]
disabled = false
format = "[$symbol$status]($style) "
symbol = "✘ "
style = "bold red"
EOF

# 8. Kitty config (with Nerd Font + slight transparency)
mkdir -p ~/.config/kitty
cat > ~/.config/kitty/kitty.conf << 'EOF'
font_family      JetBrainsMono Nerd Font
font_size        11.5
bold_font        auto
italic_font      auto
bold_italic_font auto

background_opacity 0.96
dynamic_background_opacity yes

cursor_shape     beam
cursor_blink_interval 0.5

enable_ligatures yes

# Optional: uncomment for Catppuccin theme (install via kitty +kitten themes later)
# include current-theme.conf
EOF

# 9. Install popular GNOME extensions via gext
echo "🧩 Installing GNOME extensions..."
~/.local/bin/gext install user-themes@gnome-shell-extensions.gcampax.github.com
~/.local/bin/gext install blur-my-shell@aunetx
~/.local/bin/gext install dash-to-dock@micxgx.gmail.com
~/.local/bin/gext install arcmenu@arcmenu.com
~/.local/bin/gext install just-perfection-desktop@just-perfection

# Enable them (some need logout)
~/.local/bin/gext enable user-themes@gnome-shell-extensions.gcampax.github.com
~/.local/bin/gext enable blur-my-shell@aunetx
~/.local/bin/gext enable dash-to-dock@micxgx.gmail.com
~/.local/bin/gext enable arcmenu@arcmenu.com

# 10. Final touches
echo 'eval "$(starship init bash)"' >> ~/.bashrc

# Set Kitty as default terminal
gsettings set org.gnome.desktop.default-applications.terminal exec 'kitty'
gsettings set org.gnome.desktop.default-applications.terminal exec-arg '--'

# Add fastfetch to .bashrc for nice greeting
echo 'fastfetch' >> ~/.bashrc

echo "✅ Setup complete!"
echo ""
echo "Now do this:"
echo "   1. Log out and log back in (or reboot)"
echo "   2. Open GNOME Tweaks → Appearance:"
echo "        • GTK Theme: Orchis-Dark"
echo "        • Icons: Papirus-Dark"
echo "        • Shell: Orchis-Dark (thanks to User Themes extension)"
echo "   3. Open Kitty → it should already look fire"
echo "   4. Customize further: gext list, starship.toml, kitty.conf"
echo ""
echo "Enjoy your new rice! 🔥"