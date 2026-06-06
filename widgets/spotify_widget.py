#!/usr/bin/env python3
"""Spotify now-playing widget. Shows artist, title, album, progress bar."""

import atexit
import os
import subprocess
from datetime import datetime

from common import disable_mouse, enable_mouse, poll_click
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console(width=56, highlight=False)

REFRESH_INTERVAL = 1  # seconds


def _fmt_duration(ms: int) -> str:
    """Format milliseconds as M:SS."""
    total_seconds = ms // 1_000_000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def _progress_bar(pct: float, width: int = 20) -> str:
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


def render() -> Text:
    track = _fetch_track()
    content_lines = 5  # status + artist/title + album + progress + time

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
    if len(artist_title) > 50:
        artist_title = artist_title[:47] + "..."

    album = track["album"]
    if len(album) > 50:
        album = album[:47] + "..."

    pos_str = _fmt_duration(track["position"])
    len_str = _fmt_duration(track["length"])
    progress = _progress_bar(track["pct"], width=30)

    text.append(f"    {status_icon}  ", style="bold green")
    text.append(f"{artist_title}\n", style="bold")
    text.append(f"       {album}\n", style="dim")
    text.append(f"       {progress}\n", style="cyan")
    text.append(f"       {pos_str} / {len_str}\n")

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
                # Click → play/pause toggle
                subprocess.Popen(
                    ["playerctl", "--player=spotify", "play-pause"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
finally:
    disable_mouse()
