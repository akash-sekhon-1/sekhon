#!/bin/bash

# List of logos
logos=(
    "BlackPanther"
    "BSD"
    "Calculate"
    "CRUX_small"
    "DietPi"
    "DragonFly_old"
    "GhostFreak"
    "GNU"
    "Linux"
    "OSX"
    "Minix"
    "openbsd"
    "Panwah"
    "SalentOS"
    "Scientific"
    "Slitaz"
    "Sulin"
    "Xenia_old"
)

# Get the number of logos
num_logos=${#logos[@]}

# Generate a random index
random_index=$((RANDOM % num_logos))

# Select the random logo
random_logo="${logos[$random_index]}"

# Run fastfetch with the random logo
if command -v fastfetch &>/dev/null; then
    fastfetch --logo "$random_logo" --structure " "
fi