from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from telestream import web


def _client(tmp_path, monkeypatch):
    web.db.path = str(tmp_path / "test.db")

    fake_application = AsyncMock()
    fake_application.updater = AsyncMock()
    monkeypatch.setattr(web, "build_application", lambda settings, db: fake_application)

    return TestClient(web.app)


def test_healthz(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    with client:
        resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_status_and_playlist_empty(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    with client:
        status = client.get("/status")
        assert status.json()["entries"] == 0

        playlist = client.get("/playlist.m3u")
        assert playlist.status_code == 200
        assert playlist.headers["content-type"].startswith("audio/x-mpegurl")
        assert playlist.text == "#EXTM3U\n"


def test_playlist_reflects_db(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    with client:
        web.db.add_entry("https://example.com/a.m3u8", "Show A", 1)
        playlist = client.get("/playlist.m3u")
    assert "https://example.com/a.m3u8" in playlist.text
    assert "Show A" in playlist.text
