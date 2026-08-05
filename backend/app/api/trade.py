from fastapi import APIRouter
from fastapi import HTTPException

from app.schemas.decision import DecisionContext
from app.schemas.trade import StopLossRequest
from app.schemas.trade import TakeProfitRequest
from app.schemas.trade import TicketRequest
from app.services.trade_executor import TradeExecutor

router = APIRouter(prefix="/trade", tags=["Trade"])


def _result_or_http(result):
    if result.success:
        return result

    status_code = 400

    if result.error in {"ConnectionError"}:
        status_code = 503
    elif result.error in {"TradeDisabled", "MarketClosed"}:
        status_code = 409
    elif result.error in {"BrokerRejected"}:
        status_code = 502
    elif result.error in {"InsufficientMargin"}:
        status_code = 409

    raise HTTPException(status_code=status_code, detail=result.model_dump())


@router.post("/buy")
async def buy(decision: DecisionContext):
    result = TradeExecutor().executeBuy(decision)
    return _result_or_http(result)


@router.post("/sell")
async def sell(decision: DecisionContext):
    result = TradeExecutor().executeSell(decision)
    return _result_or_http(result)


@router.post("/close")
async def close(request: TicketRequest):
    result = TradeExecutor().closePosition(request.ticket)
    return _result_or_http(result)


@router.post("/modify/sl")
async def modify_stop_loss(request: StopLossRequest):
    result = TradeExecutor().modifyStopLoss(request.ticket, request.stopLoss)
    return _result_or_http(result)


@router.post("/modify/tp")
async def modify_take_profit(request: TakeProfitRequest):
    result = TradeExecutor().modifyTakeProfit(request.ticket, request.takeProfit)
    return _result_or_http(result)


@router.post("/cancel")
async def cancel(request: TicketRequest):
    result = TradeExecutor().cancelPendingOrder(request.ticket)
    return _result_or_http(result)