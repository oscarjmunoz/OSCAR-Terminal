from fastapi import APIRouter
from fastapi import HTTPException

from pydantic import BaseModel

from app.schemas.decision import DecisionContext
from app.services.decision_center import DecisionCenter
from app.services.operational_analysis import LiveAnalysisRequest
from app.services.operational_analysis import OperationalAnalysisError
from app.services.operational_analysis import OperationalAnalysisService

router = APIRouter(prefix="/decision", tags=["Decision Center"])


class LiveDecisionPayload(BaseModel):
    symbol: str
    timeframe: str = "M5"


@router.post("/report")
async def report(decision: DecisionContext):
    return DecisionCenter.build_report(decision)


@router.post("/live-report")
async def live_report(payload: LiveDecisionPayload):
    try:
        return OperationalAnalysisService.build_report(
            LiveAnalysisRequest(
                symbol=payload.symbol,
                timeframe=payload.timeframe,
            )
        )
    except OperationalAnalysisError as error:
        raise HTTPException(
            status_code=400,
            detail={
                "code": error.code,
                "message": error.message,
            },
        ) from error
