from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str
    channel_id: str  # numeric channel id (e.g. -1001234567890) or "@channelusername"
    db_path: str = "/data/telestream.db"
    host: str = "0.0.0.0"
    port: int = 8080
    public_url: str | None = None
    log_level: str = "INFO"
    playlist_name: str = "Move to Jellyfin"


def get_settings() -> Settings:
    return Settings()
