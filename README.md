# TeleStreamM3UBot

Watches a private Telegram channel ("Move to Jellyfin") for posts containing
HTTP(S) stream URLs, and serves them as a live-updating M3U playlist that
Jellyfin can add as an M3U/IPTV tuner. No media is ever downloaded — only the
URL and a derived title are stored.

```
"Move to Jellyfin" channel -> TeleStreamM3UBot -> playlist.m3u -> Jellyfin -> stream URL directly
```

## How it works

- The bot (`@TeleStreamM3UBot`) must already be an **admin** of the channel —
  Telegram only delivers `channel_post` updates to admin bots.
- Only **new** posts are processed (Bot API can't read channel history). To
  add an old stream, re-post it.
- Each post's text/caption is scanned for `http(s)://` URLs. For each URL a
  title is derived from the first non-URL line of the post, falling back to
  the URL's filename, falling back to "Stream".
- URLs are deduplicated by exact match in SQLite.
- `GET /playlist.m3u` renders the current playlist from the database on every
  request — there's no separate "regenerate" step to run.

## Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | yes | From `@BotFather` |
| `CHANNEL_ID` | yes | Numeric channel id (`-100...`) or `@username` |
| `DB_PATH` | no | Default `/data/telestream.db` |
| `HOST` / `PORT` | no | Default `0.0.0.0:8080` |
| `PUBLIC_URL` | no | Used only to show a full URL in `/status` |
| `LOG_LEVEL` | no | Default `INFO` |
| `PLAYLIST_NAME` | no | Used as the M3U `group-title` |

Finding your channel's numeric id: forward any message from the channel to
`@JsonDumpBot` (or similar) and read `forward_from_chat.id`.

## Run with Docker

```bash
cp .env.example .env   # then edit it
docker compose up --build
```

- Playlist: `http://<host>:8080/playlist.m3u`
- Status: `http://<host>:8080/status`
- Health: `http://<host>:8080/healthz`

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env   # then edit it
uv run python -m telestream
```

## Tests

```bash
uv sync --extra dev
uv run pytest
```

## Jellyfin setup

Dashboard → Live TV → Tuner Devices → Add → **M3U Tuner** → URL:
`http://<host>:8080/playlist.m3u`. Each new channel post shows up as a channel
after Jellyfin's next guide refresh.

## Extending this later

The layers are split so each of these is additive, not a rewrite:

- **Metadata/posters** — add nullable columns to `entries` and a `tvg-logo`
  attribute in `playlist.render()`.
- **Movie/series organization** — add a `kind` column, group by it, or emit
  multiple playlists / `.strm` files.
- **Stremio support** — a new route in `web.py` reading the same
  `db.list_active()`, formatted as a Stremio addon manifest/catalog instead of
  M3U.
- **Direct HTTP streaming/proxying** — a route that streams the stored URL
  through `httpx` instead of redirecting, if you need to hide origin URLs or
  add auth headers.
- **Authentication** — a FastAPI dependency on `/playlist.m3u` (e.g. a
  `?token=` query param check).
- **Richer Telegram handling** (albums, edited posts, multiple channels) —
  additional handlers in `bot.py`; the DB and playlist layers don't change.
