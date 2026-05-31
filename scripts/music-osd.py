#!/usr/bin/env python3
"""Custom music OSD with album art for driftwm using GTK4 + Layer Shell."""

import os
import sys

# Fix gtk4-layer-shell linking order
if not os.environ.get('LD_PRELOAD', '').count('libgtk4-layer-shell'):
    os.environ['LD_PRELOAD'] = '/usr/lib/libgtk4-layer-shell.so'
    os.execv(sys.executable, [sys.executable] + sys.argv)

import gi
import subprocess
import urllib.request
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gtk4LayerShell, GLib, GdkPixbuf

COVER_PATH = "/tmp/driftwm-music-cover.jpg"
PREV_TRACK = None


class MusicOsd(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_default_size(400, 80)
        self.set_decorated(False)

        # Layer shell setup
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.TOP)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.TOP, 60)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
        Gtk4LayerShell.set_namespace(self, "music-osd")
        Gtk4LayerShell.auto_exclusive_zone_enable(self)

        # Content box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(16)
        box.set_margin_end(16)

        self.image = Gtk.Image()
        self.image.set_pixel_size(56)
        self.image.set_size_request(56, 56)
        box.append(self.image)

        self.label = Gtk.Label()
        self.label.set_xalign(0)
        self.label.set_max_width_chars(30)
        self.label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        box.append(self.label)

        self.set_child(box)

        self.timeout_id = None
        self.set_visible(False)

    def show_track(self, artist: str, title: str, cover_url: str | None):
        global PREV_TRACK
        text = f"{artist}\n{title}"
        self.label.set_markup(f"<b>{GLib.markup_escape_text(artist)}</b>\n{GLib.markup_escape_text(title)}")

        if cover_url:
            try:
                urllib.request.urlretrieve(cover_url, COVER_PATH)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(COVER_PATH, 56, 56, True)
                texture = Gdk.Texture.new_for_pixbuf(pixbuf)
                self.image.set_from_paintable(texture)
            except Exception:
                self.image.set_from_icon_name("audio-x-generic")
        else:
            self.image.set_from_icon_name("audio-x-generic")

        self.present()

        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
        self.timeout_id = GLib.timeout_add_seconds(3, self._hide)

    def _hide(self):
        self.set_visible(False)
        self.timeout_id = None
        return GLib.SOURCE_REMOVE


def playerctl_loop():
    global PREV_TRACK
    osd = MusicOsd()

    def on_activate(app):
        pass  # window managed manually

    app = Gtk.Application(application_id="dev.driftwm.music-osd")
    app.connect("activate", on_activate)

    def run_loop():
        global PREV_TRACK
        proc = subprocess.Popen(
            ["playerctl", "--player=spotify", "metadata", "--format", "{{artist}}␟{{title}}␟{{mpris:artUrl}}", "--follow"],
            stdout=subprocess.PIPE,
            text=True,
        )
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            parts = line.split("␟")
            if len(parts) < 2:
                continue
            artist, title = parts[0], parts[1]
            cover = parts[2] if len(parts) > 2 else None
            track_id = f"{artist} - {title}"
            if track_id == PREV_TRACK:
                continue
            PREV_TRACK = track_id
            GLib.idle_add(lambda a=artist, t=title, c=cover: osd.show_track(a, t, c))

    threading.Thread(target=run_loop, daemon=True).start()
    app.run(None)


if __name__ == "__main__":
    playerctl_loop()
