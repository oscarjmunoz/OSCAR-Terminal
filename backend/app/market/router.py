from fastapi import APIRouter
from fastapi import HTTPException

from app.market.service import MarketService

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


@router.get("/status")
async def terminal_status():
    return MarketService.terminal_status()


@router.get("/tick/{symbol}")
async def latest_tick(symbol: str):

    tick = MarketService.latest_tick(symbol)

    if tick is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to obtain Tick.",
        )

    return tick


@router.get("/candles/{symbol}/{timeframe}")
async def candles(
    symbol: str,
    timeframe: str,
    count: int = 200,
):

    data = MarketService.candles(
        symbol,
        timeframe,
        count,
    )

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to load candles.",
        )

    return data