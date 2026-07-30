from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "OSCAR Terminal"
    APP_VERSION: str = "0.1.0-alpha"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///../database/oscar.db"

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
    )


settings = Settings()