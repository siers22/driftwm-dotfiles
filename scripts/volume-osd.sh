#!/bin/bash
# Volume OSD for driftwm + swaync
# Shows a top notification with a progress bar that replaces itself on change.

SINK="@DEFAULT_AUDIO_SINK@"

case "$1" in
    up)   wpctl set-volume "$SINK" 5%+ ;;
    down) wpctl set-volume "$SINK" 5%- ;;
    mute) wpctl set-mute "$SINK" toggle ;;
    *)    echo "usage: $0 up|down|mute" >&2; exit 1 ;;
esac

# Parse current volume state:
#   Volume: 0.45
#   Volume: 0.45 [MUTED]
read -r _ vol muted <<< "$(wpctl get-volume "$SINK")"
percent=$(awk "BEGIN {printf \"%d\", $vol * 100}")

if [ "$muted" = "[MUTED]" ] || [ "$percent" -eq 0 ]; then
    icon="audio-volume-muted"
    text="Muted"
    value=0
else
    if [ "$percent" -lt 30 ]; then
        icon="audio-volume-low"
    elif [ "$percent" -lt 70 ]; then
        icon="audio-volume-medium"
    else
        icon="audio-volume-high"
    fi
    text="Volume ${percent}%"
    value=$percent
fi

notify-send \
    -i "$icon" \
    -h "int:value:$value" \
    -h "string:x-canonical-private-synchronous:volume-osd" \
    -t 2000 \
    -u low \
    "$text"
