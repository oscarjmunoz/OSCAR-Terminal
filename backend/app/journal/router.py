from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from app.journal.models import JournalEntryCreate
from app.journal.models import JournalFilterCriteria
from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.service import JournalNotFoundError
from app.journal.service import JournalService

router = APIRouter(prefix="/journal", tags=["Journal"])

_journal_service = JournalService()


def get_journal_service() -> JournalService:
    return _journal_service


def _not_found(error: JournalNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail={"message": "Journal entry not found", "id": error.entry_id})


@router.post("")
async def create_entry(payload: JournalEntryCreate, service: JournalService = Depends(get_journal_service)):
    return service.createEntry(payload)


@router.get("")
async def list_entries(
    service: JournalService = Depends(get_journal_service),
    q: str | None = Query(default=None, alias="q"),
    symbol: str | None = None,
    timeframe: str | None = None,
    session: str | None = None,
    traderDecision: TraderDecision | None = None,
    tradeOutcome: TradeOutcome | None = None,
    tag: str | None = None,
):
    criteria = JournalFilterCriteria(
        symbol=symbol,
        timeframe=timeframe,
        session=session,
        traderDecision=traderDecision,
        tradeOutcome=tradeOutcome,
        tag=tag,
    )
    return service.listEntries(filters=criteria if any(value is not None for value in criteria.model_dump().values()) else None, query=q)


@router.get("/{entry_id}")
async def get_entry(entry_id: str, service: JournalService = Depends(get_journal_service)):
    try:
        return service.getEntry(entry_id)
    except JournalNotFoundError as error:
        raise _not_found(error) from error


@router.patch("/{entry_id}")
async def update_entry(entry_id: str, payload: JournalOutcomeUpdate, service: JournalService = Depends(get_journal_service)):
    try:
        return service.updateOutcome(entry_id, payload)
    except JournalNotFoundError as error:
        raise _not_found(error) from error


@router.delete("/{entry_id}")
async def delete_entry(entry_id: str, service: JournalService = Depends(get_journal_service)):
    try:
        return service.deleteEntry(entry_id)
    except JournalNotFoundError as error:
        raise _not_found(error) from error
