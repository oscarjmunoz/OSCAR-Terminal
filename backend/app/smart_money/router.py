# backend/app/smart_money/router.py
# REEMPLAZAR COMPLETAMENTE EL ARCHIVO

from fastapi import APIRouter

from app.smart_money.service import SmartMoneyService

router = APIRouter(
    prefix="/smart-money",
    tags=["Smart Money"],
)


@router.get("/swings/{symbol}")
async def swings(
    symbol: str,
    timeframe: str = "M5",
    candles: int = 300,
    left: int = 3,
    right: int = 3,
):

    return SmartMoneyService.swings(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        left=left,
        right=right,
    )


@router.get("/structure/{symbol}")
async def structure(
    symbol: str,
    timeframe: str = "M5",
    candles: int = 300,
    left: int = 3,
    right: int = 3,
):

    result = SmartMoneyService.structure(
        symbol=symbol,
        timeframe=timeframe,
        candles=candles,
        left=left,
        right=right,
    )

    if result is None:
        return {
            "trend": "UNKNOWN",
            "last_high": None,
            "last_low": None,
            "bos": False,
            "choch": False,
            "mss": False,
        }

    return {
        "trend": result.trend,
        "last_high": result.last_high,
        "last_low": result.last_low,
        "bos": result.bos,
        "choch": result.choch,
        "mss": result.mss,
    }