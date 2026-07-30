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
            detail="Symbol not available or MT5 disconnected.",
        )

    return tick