from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgres://localhost:5432/nfs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
