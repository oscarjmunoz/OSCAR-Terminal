from fastapi import APIRouter

from app.analytics.router import router as analytics_router
from app.api.decision import router as decision_router
from app.api.health import router as health_router
from app.api.info import router as info_router
from app.playbook.router import router as playbook_router
from app.journal.router import router as journal_router
from app.api.trade import router as trade_router
from app.api.system import router as system_router
from app.market.router import router as market_router
from app.smart_money.router import router as smart_money_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(info_router)
api_router.include_router(system_router)
api_router.include_router(decision_router)
api_router.include_router(playbook_router)
api_router.include_router(journal_router)
api_router.include_router(analytics_router)
api_router.include_router(trade_router)
api_router.include_router(market_router)
api_router.include_router(smart_money_router)