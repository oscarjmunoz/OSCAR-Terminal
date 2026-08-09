from fastapi import APIRouter

from app.execution.schemas import ExecutionRequest
from app.execution.schemas import ExecutionResult
from app.execution.service import ExecutionService

router = APIRouter(prefix="/execution", tags=["Execution"])


@router.post("/prepare", response_model=ExecutionResult)
async def prepare_trade(request: ExecutionRequest):
    return ExecutionService.prepare(request)
