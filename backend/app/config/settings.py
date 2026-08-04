from pathlib import Path

from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "database" / "oscar.db"

DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):

    APP_NAME: str = "OSCAR Terminal"
    APP_VERSION: str = "0.1.0-alpha"

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    healthCheckInterval: int = 5
    pipelineTimeout: int = 30
    tickTimeout: int = 15
    maxSlippage: int = 20
    magicNumber: int = 240803
    defaultDeviation: int = 10

    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH.as_posix()}"


settings = Settings()