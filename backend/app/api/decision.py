from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel

from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.playbook.router import get_playbook_service
from app.playbook.service import PlaybookService
from app.schemas.decision import DecisionContext
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeRequest
from app.schemas.decision_execution_bridge import DecisionExecutionBridgeResult
from app.services.decision_execution_bridge import DecisionExecutionBridge
from app.services.decision_center import DecisionCenter
from app.services.operational_analysis import LiveAnalysisRequest
from app.services.operational_analysis import OperationalAnalysisError
from app.services.operational_analysis import OperationalAnalysisService
from app.services.paper_execution_service import PaperExecutionService
from app.services.paper_execution_service import get_paper_execution_service
from app.services.trade_executor import TradeExecutor

router = APIRouter(prefix="/decision", tags=["Decision Center"])


class LiveDecisionPayload(BaseModel):
    symbol: str
    timeframe: str = "M5"


def get_decision_execution_bridge(
    playbook_service: PlaybookService = Depends(get_playbook_service),
    journal_service: JournalService = Depends(get_journal_service),
    paper_execution_service: PaperExecutionService = Depends(get_paper_execution_service),
) -> DecisionExecutionBridge:
    return DecisionExecutionBridge(
        playbook_service=playbook_service,
        journal_service=journal_service,
        trade_executor=TradeExecutor(),
        paper_execution_service=paper_execution_service,
    )


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


@router.post("/execute", response_model=DecisionExecutionBridgeResult)
async def execute_decision(
    payload: DecisionExecutionBridgeRequest,
    bridge: DecisionExecutionBridge = Depends(get_decision_execution_bridge),
):
    return bridge.execute(payload)
