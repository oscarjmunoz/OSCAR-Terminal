from fastapi import APIRouter

from app.opportunity.schemas import OpportunityQueueResponse
from app.opportunity.service import OpportunityService
from app.scanner import router as scanner_router_module

router = APIRouter(prefix="/opportunity", tags=["Opportunity"])

_service = OpportunityService(scanner_service=scanner_router_module._service)


@router.get("/queue", response_model=OpportunityQueueResponse)
async def get_opportunity_queue() -> OpportunityQueueResponse:
    return _service.get_queue()
