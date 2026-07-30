from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.info import router as info_router
from app.api.system import router as system_router
from app.market.router import router as market_router
from app.smart_money.router import router as smart_money_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(info_router)
api_router.include_router(system_router)
api_router.include_router(market_router)
api_router.include_router(smart_money_router)