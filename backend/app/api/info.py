from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter(tags=["Info"])


@router.get("/info")
async def info():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development",
        "engines": {
            "market": False,
            "smart_money": False,
            "probability": False,
            "risk": False,
            "ai": False,
            "journal": False,
        },
    }