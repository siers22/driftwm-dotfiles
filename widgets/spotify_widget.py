#!/usr/bin/env python3
"""Spotify now-playing widget. Shows artist, title, album, progress bar + controls."""

import atexit
import os
import subprocess
from datetime import datetime

from common import disable_mouse, enable_mouse, get_volume, poll_click
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console(width=63, highlight=False)

# Click zones for buttons: (start_x, end_x, action)
# These are approximate terminal column ranges for each button.
BUTTONS_X = {
    "shuffle": (40, 44),
    "prev": (45, 49),
    "play": (50, 54),
    "next": (55, 59),
    "mute": (60, 63),
}

BUTTONS_LABELS = {
    "shuffle": "🔀",
    "prev": "⏮",
    "play": "⏸",
    "pause": "▶",
    "next": "⏭",
    "mute": "🔇",
    "unmute": "🔊",
}


def _fmt_duration(ms: int) -> str:
    """Format milliseconds as M:SS."""
    total_seconds = ms // 1_000_000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def _progress_bar(pct: float, width: int = 30) -> str:
    """Render a thin progress bar."""
    pct = max(0.0, min(100.0, pct))
    filled = round(pct / 100 * width)
    return "━" * filled + "─" * (width - filled)


def _fetch_track() -> dict | None:
    """Fetch current track info from Spotify via playerctl."""
    try:
        result = subprocess.run(
            [
                "playerctl",
                "--player=spotify",
                "metadata",
                "--format",
                "{{artist}}\t{{title}}\t{{album}}\t{{position}}\t{{mpris:length}}\t{{status}}",
            ],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        parts = result.stdout.strip().split("\t")
        if len(parts) < 6:
            return None
        pos = int(parts[3]) if parts[3].isdigit() else 0
        length = int(parts[4]) if parts[4].isdigit() else 1
        return {
            "artist": parts[0],
            "title": parts[1],
            "album": parts[2],
            "position": pos,
            "length": length,
            "status": parts[5],
            "pct": (pos / length * 100) if length > 0 else 0,
        }
    except Exception:
        return None


def _get_buttons(status: str, muted: bool) -> str:
    """Render the control buttons row."""
    play_icon = BUTTONS_LABELS["play"] if status.lower() == "playing" else BUTTONS_LABELS["pause"]
    mute_icon = BUTTONS_LABELS["mute"] if muted else BUTTONS_LABELS["unmute"]
    return f"{BUTTONS_LABELS['shuffle']}  {BUTTONS_LABELS['prev']}  {play_icon}  {BUTTONS_LABELS['next']}  {mute_icon}"


def _dispatch_button(name: str) -> None:
    """Execute playerctl command for a button."""
    cmds = {
        "shuffle": ["playerctl", "--player=spotify", "shuffle"],
        "prev": ["playerctl", "--player=spotify", "previous"],
        "play": ["playerctl", "--player=spotify", "play-pause"],
        "pause": ["playerctl", "--player=spotify", "play-pause"],
        "next": ["playerctl", "--player=spotify", "next"],
        "mute": ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"],
        "unmute": ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"],
    }
    cmd = cmds.get(name)
    if cmd:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _button_from_x(x: int, status: str, muted: bool) -> str | None:
    """Map terminal x coordinate to button name."""
    for name, (start, end) in BUTTONS_X.items():
        if start <= x <= end:
            if name == "play":
                return "pause" if status.lower() != "playing" else "play"
            if name == "mute":
                return "unmute" if muted else "mute"
            return name
    return None


def render() -> Text:
    track = _fetch_track()
    vol, muted = get_volume()
    content_lines = 6  # status + artist/title + album + progress + time + buttons

    try:
        term_h = os.get_terminal_size().lines
    except OSError:
        term_h = 6
    top_pad = max((term_h - content_lines) // 2, 0)

    text = Text()
    text.append("\n" * top_pad)

    if track is None:
        text.append("         Spotify is not running\n")
        return text

    status_icon = "▶" if track["status"].lower() == "playing" else "⏸"
    artist_title = f"{track['artist']} — {track['title']}"
    if len(artist_title) > 54:
        artist_title = artist_title[:51] + "..."

    album = track["album"]
    if len(album) > 54:
        album = album[:51] + "..."

    pos_str = _fmt_duration(track["position"])
    len_str = _fmt_duration(track["length"])
    progress = _progress_bar(track["pct"], width=30)
    buttons = _get_buttons(track["status"], muted)

    text.append(f"    {status_icon}  ", style="bold green")
    text.append(f"{artist_title}\n", style="bold")
    text.append(f"       {album}\n", style="dim")
    text.append(f"       {progress}\n", style="cyan")
    text.append(f"       {pos_str} / {len_str}\n")
    # Right-align buttons
    text.append(f"{'':>34}{buttons}\n")

    return text


atexit.register(disable_mouse)
enable_mouse()
console.clear()
try:
    with Live(render(), console=console, refresh_per_second=1) as live:
        while True:
            live.update(render())
            click = poll_click(1.0)
            if click is not None:
                x, y = click
                track = _fetch_track()
                if track is not None:
                    _, muted = get_volume()
                    btn = _button_from_x(x, track["status"], muted)
                    if btn:
                        _dispatch_button(btn)
                    else:
                        # Click outside buttons → play/pause
                        subprocess.Popen(
                            ["playerctl", "--player=spotify", "play-pause"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
finally:
    disable_mouse()
