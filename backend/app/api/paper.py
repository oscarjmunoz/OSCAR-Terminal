from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.journal.router import get_journal_service
from app.journal.service import JournalService
from app.schemas.decision_execution_bridge import PaperPositionCloseSummary
from app.schemas.decision_execution_bridge import PaperPositionUpdateSummary
from app.services.paper_execution_service import PaperExecutionService
from app.services.paper_execution_service import PaperMarketTickUnavailableError
from app.services.paper_execution_service import PaperPositionNotFoundError
from app.services.paper_execution_service import get_paper_execution_service

router = APIRouter(prefix="/paper", tags=["Paper Execution"])


def _position_not_found(error: PaperPositionNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail={"message": "Paper position not found", "id": error.position_id})


def _tick_unavailable(error: PaperMarketTickUnavailableError) -> HTTPException:
    return HTTPException(status_code=409, detail={"message": "Latest tick unavailable", "symbol": error.symbol})


@router.post("/positions/{position_id}/update", response_model=PaperPositionUpdateSummary)
async def update_paper_position(
    position_id: str,
    service: PaperExecutionService = Depends(get_paper_execution_service),
):
    try:
        return service.update_position(position_id=position_id)
    except PaperPositionNotFoundError as error:
        raise _position_not_found(error) from error
    except PaperMarketTickUnavailableError as error:
        raise _tick_unavailable(error) from error


@router.post("/positions/{position_id}/close", response_model=PaperPositionCloseSummary)
async def close_paper_position(
    position_id: str,
    service: PaperExecutionService = Depends(get_paper_execution_service),
    journal_service: JournalService = Depends(get_journal_service),
):
    try:
        return service.close_position(position_id=position_id, journal_service=journal_service)
    except PaperPositionNotFoundError as error:
        raise _position_not_found(error) from error
    except PaperMarketTickUnavailableError as error:
        raise _tick_unavailable(error) from error