from telestream.db import Entry
from telestream.playlist import render


def test_render_empty():
    assert render([], "My Playlist") == "#EXTM3U\n"


def test_render_entries():
    entries = [
        Entry(1, "https://example.com/a.m3u8", "Show A", None, "t", True),
        Entry(2, "https://example.com/b.m3u8", "Show B", None, "t", True),
    ]
    out = render(entries, "Move to Jellyfin")
    assert out == (
        "#EXTM3U\n"
        '#EXTINF:-1 tvg-id="ts-1" tvg-name="Show A" group-title="Move to Jellyfin",Show A\n'
        "https://example.com/a.m3u8\n"
        '#EXTINF:-1 tvg-id="ts-2" tvg-name="Show B" group-title="Move to Jellyfin",Show B\n'
        "https://example.com/b.m3u8\n"
    )


def test_render_sanitizes_commas_and_newlines():
    entries = [Entry(1, "https://example.com/a.m3u8", "Show, A\nExtra", None, "t", True)]
    out = render(entries, "G")
    extinf_line = out.splitlines()[0 + 1]
    assert extinf_line.count(",") == 1
    assert extinf_line.endswith(",Show  A Extra")
