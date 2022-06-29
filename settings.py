from pydantic import BaseSettings
import pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
WEBUI_ROOT = ROOT / "webui"


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/nfs"
    redis_url: str = 'redis://localhost:6379/0'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
