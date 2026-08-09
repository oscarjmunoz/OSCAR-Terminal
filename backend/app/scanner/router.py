from fastapi import APIRouter

from app.scanner.repository import SqlAlchemyScannerRepository
from app.scanner.schemas import OpportunityListResponse
from app.scanner.scheduler import ScannerScheduler
from app.scanner.service import ScannerService

router = APIRouter(prefix="/scanner", tags=["Scanner"])

_repository = SqlAlchemyScannerRepository()
_service = ScannerService(repository=_repository)
_scheduler = ScannerScheduler(service=_service, interval_seconds=30)


@router.on_event("startup")
async def _start_scanner_scheduler() -> None:
    _scheduler.start()


@router.on_event("shutdown")
async def _stop_scanner_scheduler() -> None:
    _scheduler.stop()


@router.get("/opportunities", response_model=OpportunityListResponse)
async def list_opportunities() -> OpportunityListResponse:
    opportunities = _service.list_opportunities()

    if not opportunities:
        opportunities = _service.refresh_opportunities()

    return OpportunityListResponse(opportunities=opportunities)
