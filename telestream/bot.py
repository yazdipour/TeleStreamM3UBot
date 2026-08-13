import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from telestream.config import Settings
from telestream.db import Database
from telestream.extract import derive_title, find_urls

logger = logging.getLogger(__name__)


def _channel_filter(channel_id: str) -> filters.BaseFilter:
    chat = int(channel_id) if channel_id.lstrip("-").isdigit() else channel_id
    return filters.Chat(chat_id=chat) if isinstance(chat, int) else filters.Chat(username=chat.lstrip("@"))


def build_application(settings: Settings, db: Database) -> Application:
    application = Application.builder().token(settings.telegram_bot_token).build()

    channel_filter = _channel_filter(settings.channel_id) & filters.UpdateType.CHANNEL_POST

    async def on_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        msg = update.channel_post
        text = msg.text or msg.caption
        urls = find_urls(text)
        if not urls:
            return
        added = 0
        for i, url in enumerate(urls, start=1):
            title = derive_title(text, url, index=i)
            if db.add_entry(url, title, msg.message_id):
                added += 1
        logger.info("post %s: %d url(s) found, %d new", msg.message_id, len(urls), added)

    application.add_handler(MessageHandler(channel_filter, on_channel_post))
    return application
