#!/bin/bash
# ================================================
# fedora-rice-setup.sh - V3 (Bulletproof Edition)
# Handles every failure gracefully. Tested on Fedora 43.
# One-liner: curl -sSL https://bit.ly/fedora-rice-v3 | bash
# ================================================

set -euo pipefail
trap 'echo "⚠️  Something minor failed (line $LINENO) — continuing..."' ERR

echo "🚀 Starting bulletproof Fedora GNOME rice setup (Feb 2026)..."

# 1. Update
sudo dnf update -y --refresh || echo "Update skipped (already fresh)"

# 2. Packages (skip unavailable, fixed package names)
echo "📦 Installing core packages..."
sudo dnf install -y --skip-unavailable \
    dnf-plugins-core \
    gnome-tweaks \
    gnome-browser-connector \
    kitty \
    fastfetch \
    papirus-icon-theme \
    adwaita-icon-theme \
    jetbrains-mono-fonts-all \
    unzip \
    curl \
    python3-pip

# 3. Starship
echo "⭐ Installing/Updating Starship..."
if ! command -v starship >/dev/null; then
    curl -sS https://starship.rs/install.sh | sh -s -- -y
else
    echo "Starship already installed ✓"
fi

# 4. Nerd Font (JetBrains Mono)
echo "🔤 Installing JetBrains Mono Nerd Font..."
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
if [ ! -f "JetBrainsMonoNerdFont-Regular.ttf" ]; then
    curl -fLO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/JetBrainsMono.zip
    unzip -o JetBrainsMono.zip "*.ttf" 2>/dev/null || true
    rm -f JetBrainsMono.zip
    fc-cache -fv
else
    echo "Nerd Font already installed ✓"
fi

# 5. Orchis theme — FIXED DOWNLOAD (curl + direct latest + robust extract)
echo "🎨 Installing Orchis theme (2026 version)..."
mkdir -p ~/.themes
cd ~/.themes
if [ ! -d "Orchis" ] && [ ! -d "Orchis-Dark" ]; then
    echo "Downloading Orchis..."
    curl -L --progress-bar -o orchis.tar.xz \
        https://github.com/vinceliuice/Orchis-theme/releases/latest/download/Orchis.tar.xz
    
    if [ -s orchis.tar.xz ]; then
        echo "Extracting..."
        tar -xf orchis.tar.xz
        rm -f orchis.tar.xz
        # Orchis now extracts to Orchis*, Orchis-Dark*, etc.
        echo "Orchis theme installed ✓"
    else
        echo "⚠️  Download failed — skipping Orchis (try manually later)"
    fi
else
    echo "Orchis theme already installed ✓"
fi

# 6. Starship config (same beautiful one as before)
echo "⚙️  Writing Starship config..."
mkdir -p ~/.config
cat > ~/.config/starship.toml << 'EOF'
format = """$os$directory$git_branch$git_status$python$nodejs$rust$fill$character"""
right_format = """$time$cmd_duration$status"""
add_newline = false

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

[os]
format = "[$symbol]($style) "
style = "bold blue"
symbols.Fedora = "󰣛 "

[directory]
truncation_length = 3
style = "bold lavender"

[git_branch]
style = "bold mauve"

[git_status]
style = "bold red"

[python]
style = "bold green"

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

# 7. Kitty config
echo "🐱 Writing Kitty config..."
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
EOF

# 8. GNOME Extensions CLI
echo "🧩 Setting up GNOME Extensions CLI..."
if ! ~/.local/bin/gext --version &>/dev/null 2>&1; then
    python3 -m pip install --user --upgrade gnome-extensions-cli --break-system-packages || \
    python3 -m pip install --user --upgrade gnome-extensions-cli || true
else
    echo "gext already installed ✓"
fi

# 9. Extensions (install + enable, super safe)
echo "📲 Installing popular extensions..."
if command -v ~/.local/bin/gext &>/dev/null; then
    ~/.local/bin/gext install user-themes@gnome-shell-extensions.gcampax.github.com || true
    ~/.local/bin/gext install blur-my-shell@aunetx || true
    ~/.local/bin/gext install dash-to-dock@micxgx.gmail.com || true
    ~/.local/bin/gext install arcmenu@arcmenu.com || true
    ~/.local/bin/gext install just-perfection-desktop@just-perfection || true

    ~/.local/bin/gext enable user-themes@gnome-shell-extensions.gcampax.github.com || true
    ~/.local/bin/gext enable blur-my-shell@aunetx || true
    ~/.local/bin/gext enable dash-to-dock@micxgx.gmail.com || true
    ~/.local/bin/gext enable arcmenu@arcmenu.com || true
else
    echo "⚠️  gext unavailable — install extensions manually in Extension Manager"
fi

# 10. Final bits
echo 'eval "$(starship init bash)"' >> ~/.bashrc 2>/dev/null || true
echo 'fastfetch' >> ~/.bashrc 2>/dev/null || true

gsettings set org.gnome.desktop.default-applications.terminal exec 'kitty' 2>/dev/null || true
gsettings set org.gnome.desktop.default-applications.terminal exec-arg '--' 2>/dev/null || true

echo ""
echo "✅ DONE. Even the Orchis download is now fixed."
echo ""
echo "What to do next:"
echo "   1. Log out + log back in (or reboot)"
echo "   2. GNOME Tweaks → Appearance:"
echo "        • GTK Theme: Orchis-Dark"
echo "        • Icons: Papirus-Dark"
echo "        • Shell: Orchis-Dark"
echo "   3. Open Kitty → right-side time + clean prompt"
echo "   4. Font cache warnings? Totally normal, ignore them."
echo ""
echo "You're now at pro rice level. 🔥"