from telestream.extract import derive_title, find_urls


def test_find_urls_basic():
    assert find_urls("Check http://example.com/stream.m3u8 out") == [
        "http://example.com/stream.m3u8"
    ]


def test_find_urls_strips_trailing_punct():
    text = "Stream: https://example.com/a.mp4, also (https://example.com/b.mp4)."
    assert find_urls(text) == [
        "https://example.com/a.mp4",
        "https://example.com/b.mp4",
    ]


def test_find_urls_dedupes():
    text = "https://x.com/a\nhttps://x.com/a"
    assert find_urls(text) == ["https://x.com/a"]


def test_find_urls_none_and_empty():
    assert find_urls(None) == []
    assert find_urls("no urls here") == []


def test_derive_title_from_first_line():
    text = "Big Buck Bunny\nhttps://example.com/bbb.m3u8"
    assert derive_title(text, "https://example.com/bbb.m3u8") == "Big Buck Bunny"


def test_derive_title_from_url_when_no_text_line():
    text = "https://example.com/path/My_Movie-2024.mp4"
    title = derive_title(text, "https://example.com/path/My_Movie-2024.mp4")
    assert title == "My Movie 2024"


def test_derive_title_fallback():
    assert derive_title(None, "https://example.com/") == "Stream"


def test_derive_title_index_suffix():
    title = derive_title("Show\nurl1\nurl2", "https://example.com/x.mp4", index=2)
    assert title == "Show (2)"
