"""应用配置：使用 Pydantic Settings 从 .env 读取，提供默认值。"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    APP_NAME: str = "智能抽油机系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./data/pump.db"

    SECRET_KEY: str = "smart-pump-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    SIMULATION_INTERVAL_SECONDS: int = 3
    DEFAULT_DEVICE_ID: int = 1

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
