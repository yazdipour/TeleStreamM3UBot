import re
from urllib.parse import urlparse

_URL_RE = re.compile(r"https?://[^\s<>\"]+", re.IGNORECASE)
_TRAILING_PUNCT = ",.;:!?)]}>”'\""


def find_urls(text: str | None) -> list[str]:
    """Extract http(s) URLs from free-form post/caption text, deduped, order preserved."""
    if not text:
        return []
    seen: set[str] = set()
    urls: list[str] = []
    for match in _URL_RE.findall(text):
        url = match.rstrip(_TRAILING_PUNCT)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def _title_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    if "/" not in path:
        return ""  # nothing but the domain, e.g. "https://example.com/"
    tail = path.rsplit("/", 1)[-1]
    if "." in tail:
        tail = tail.rsplit(".", 1)[0]
    return re.sub(r"[._-]+", " ", tail).strip()


def derive_title(text: str | None, url: str, index: int = 1) -> str:
    """Pick a human title: first non-URL line of the post, else the URL slug, else a placeholder."""
    title = ""
    if text:
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith(("http://", "https://")):
                title = line[:120]
                break
    if not title:
        title = _title_from_url(url)
    if not title:
        title = "Stream"
    if index > 1:
        title = f"{title} ({index})"
    return title
