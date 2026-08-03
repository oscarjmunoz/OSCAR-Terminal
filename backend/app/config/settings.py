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

    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH.as_posix()}"

    SCORE_WEIGHT_LIQUIDITY: int = 15
    SCORE_WEIGHT_STRUCTURE: int = 20
    SCORE_WEIGHT_BIAS: int = 15
    SCORE_WEIGHT_ORDER_BLOCKS: int = 10
    SCORE_WEIGHT_FVG: int = 10
    SCORE_WEIGHT_RISK: int = 20
    SCORE_WEIGHT_SESSION: int = 10

    CONFIDENCE_WEIGHT_CONFLUENCE: int = 35
    CONFIDENCE_WEIGHT_CONTRADICTION: int = 20
    CONFIDENCE_WEIGHT_CONTEXT_QUALITY: int = 25
    CONFIDENCE_WEIGHT_ENGINE_CONSISTENCY: int = 20

    RISK_MAX_PERCENT: float = 1.0
    RISK_MAX_EXPOSURE_PERCENT: float = 3.0
    RISK_MIN_RR: float = 1.5

    DECISION_MIN_SCORE: int = 70
    DECISION_MIN_CONFIDENCE: int = 65

    INSTITUTIONAL_ALLOWED_SESSIONS: str = "LONDON,NEW_YORK,OVERLAP"


settings = Settings()