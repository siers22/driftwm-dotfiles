#!/bin/sh
set -eu

dir="$HOME/Pictures/Screenshots"
mkdir -p "$dir"

file="$dir/screenshot_$(date +%Y%m%d_%H%M%S).png"

geom="$(slurp 2>/dev/null)" || {
    exit 0
}

grim -g "$geom" "$file"
wl-copy < "$file"

notify-send "Screenshot" "Saved to $file and copied to clipboard" 2>/dev/null || true
