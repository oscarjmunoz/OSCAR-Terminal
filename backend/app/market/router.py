from fastapi import APIRouter

from app.market.service import MarketService

router = APIRouter(
    prefix="/market",
    tags=["Market"],
)


@router.get("/status")
async def terminal_status():

    return MarketService.terminal_status()