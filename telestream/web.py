import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse

from telestream.bot import build_application
from telestream.config import get_settings
from telestream.db import Database
from telestream.playlist import render

settings = get_settings()
logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

db = Database(settings.db_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    application = build_application(settings, db)
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=False)
    app.state.application = application
    try:
        yield
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


app = FastAPI(title="TeleStreamM3UBot", lifespan=lifespan)


@app.get("/")
def root():
    return RedirectResponse(url="/status")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/status")
def status():
    return {
        "entries": db.count(),
        "channel": settings.channel_id,
        "playlist_url": f"{settings.public_url}/playlist.m3u" if settings.public_url else "/playlist.m3u",
    }


@app.get("/playlist.m3u")
def playlist():
    body = render(db.list_active(), settings.playlist_name)
    return PlainTextResponse(
        body,
        media_type="audio/x-mpegurl",
        headers={"Content-Disposition": 'inline; filename="playlist.m3u"'},
    )
