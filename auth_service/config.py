from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent


class DBConfig(BaseModel):
    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR / "db.sqlite3"}"
    echo: bool = False


class Settings(BaseSettings):
    project_title: str
    version: str
    debug: bool
    description: str

    db_settings: DBConfig = DBConfig()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings(
    project_title="Auth Service API",
    version="0.1.0",
    debug=True,
    description="API for authentication service",
)
