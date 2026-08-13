import uvicorn

from telestream.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("telestream.web:app", host=settings.host, port=settings.port)
