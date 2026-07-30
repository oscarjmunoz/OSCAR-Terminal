from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.config.settings import DATABASE_PATH, settings

router = APIRouter(tags=["System"])


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