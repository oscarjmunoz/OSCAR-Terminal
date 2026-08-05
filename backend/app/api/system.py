from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.config.settings import DATABASE_PATH, settings
from app.market.timeframes import TIMEFRAMES
from app.schemas.operational import OperationalSettingsResponse

router = APIRouter(tags=["System"])


def _configured_symbols() -> list[str]:
    configured = [item.strip().upper() for item in settings.availableSymbols.split(",") if item.strip()]
    seen: set[str] = set()
    symbols: list[str] = []

    for symbol in configured:
        if symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)

    if settings.defaultSymbol.upper() not in seen:
        symbols.insert(0, settings.defaultSymbol.upper())

    return symbols


@router.get("/system")
async def system():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

        return {
            "database": "connected",
            "database_url": settings.DATABASE_URL,
            "engine_url": str(engine.url),
            "database_file": str(DATABASE_PATH),
        }

    except Exception as exc:
        return {
            "database": "error",
            "database_url": settings.DATABASE_URL,
            "engine_url": str(engine.url),
            "database_file": str(DATABASE_PATH),
            "exception": repr(exc),
        }


@router.get("/system/settings", response_model=OperationalSettingsResponse)
async def operational_settings():
    return OperationalSettingsResponse(
        defaultSymbol=settings.defaultSymbol.upper(),
        defaultTimeframe=settings.defaultTimeframe.upper(),
        availableSymbols=_configured_symbols(),
        availableTimeframes=list(TIMEFRAMES.keys()),
    )