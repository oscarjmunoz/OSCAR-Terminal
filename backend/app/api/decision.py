from fastapi import APIRouter

from app.schemas.decision import DecisionContext
from app.services.decision_center import DecisionCenter

router = APIRouter(prefix="/decision", tags=["Decision Center"])


@router.post("/report")
async def report(decision: DecisionContext):
    return DecisionCenter.build_report(decision)
