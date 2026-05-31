#!/bin/bash
# Auto OSD on Spotify track change using swayosd

PREV_FILE="/tmp/driftwm-media-osd-prev"

while true; do
    while read -r line; do
        [ -z "$line" ] && continue
        [ -f "$PREV_FILE" ] && [ "$(cat "$PREV_FILE" 2>/dev/null)" = "$line" ] && continue

        msg="$line"
        if [ ${#msg} -gt 60 ]; then
            msg="${msg:0:57}..."
        fi

        swayosd-client --custom-message "$msg" 2>/dev/null

        echo "$line" > "$PREV_FILE"
    done < <(playerctl --player=spotify metadata --format '{{artist}} - {{title}}' --follow 2>/dev/null)

    sleep 2
done
