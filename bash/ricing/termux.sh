#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[*] Updating packages..."
pkg update -y
pkg upgrade -y

echo "[*] Installing core tools..."
pkg install -y git curl wget unzip starship neovim tmux htop

# ---- Starship prompt ----
if ! grep -q "starship init bash" ~/.bashrc 2>/dev/null; then
    echo 'eval "$(starship init bash)"' >> ~/.bashrc
fi

# ---- Nerd Font install (JetBrainsMono Nerd Font) ----
echo "[*] Installing Nerd Font..."

mkdir -p ~/.termux
cd ~/.termux

wget -q https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip
unzip -o JetBrainsMono.zip >/dev/null

# Pick a usable TTF (Termux uses single font.ttf)
cp JetBrainsMonoNerdFont-Regular.ttf ~/.termux/font.ttf

rm -rf JetBrainsMono*

termux-reload-settings || true

# ---- Basic Starship config ----
mkdir -p ~/.config
cat > ~/.config/starship.toml << 'EOF'
format = "$directory$git_branch$character"

[directory]
style = "blue bold"
truncation_length = 3

[character]
success_symbol = "[❯](green bold)"
error_symbol = "[❯](red bold)"
EOF



echo
echo "Done."
echo "Restart Termux."
