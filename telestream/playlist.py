from telestream.db import Entry

_UNSAFE = str.maketrans({",": " ", "\n": " ", "\r": " "})


def _sanitize(title: str) -> str:
    return title.translate(_UNSAFE).strip()


def render(entries: list[Entry], playlist_name: str) -> str:
    lines = ["#EXTM3U"]
    for entry in entries:
        title = _sanitize(entry.title)
        lines.append(
            f'#EXTINF:-1 tvg-id="ts-{entry.id}" tvg-name="{title}" '
            f'group-title="{playlist_name}",{title}'
        )
        lines.append(entry.url)
    return "\n".join(lines) + "\n"
