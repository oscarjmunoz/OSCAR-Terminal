from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.playbook.models import PlaybookEvaluationRequest
from app.playbook.models import PlaybookSetupCreate
from app.playbook.models import PlaybookSetupUpdate
from app.playbook.service import PlaybookNotFoundError
from app.playbook.service import PlaybookService

router = APIRouter(prefix="/playbook", tags=["Institutional Playbook"])

_playbook_service = PlaybookService()


def get_playbook_service() -> PlaybookService:
    return _playbook_service


def _not_found(error: PlaybookNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail={"message": "Playbook setup not found", "id": error.setup_id})


@router.post("")
async def create_setup(payload: PlaybookSetupCreate, service: PlaybookService = Depends(get_playbook_service)):
    return service.createSetup(payload)


@router.get("")
async def list_setups(service: PlaybookService = Depends(get_playbook_service)):
    return service.listSetups()


@router.post("/evaluate")
async def evaluate(payload: PlaybookEvaluationRequest, service: PlaybookService = Depends(get_playbook_service)):
    return service.evaluate(payload)


@router.get("/statistics")
async def statistics(service: PlaybookService = Depends(get_playbook_service)):
    return service.getStatistics()


@router.get("/{setup_id}")
async def get_setup(setup_id: str, service: PlaybookService = Depends(get_playbook_service)):
    try:
        return service.getSetup(setup_id)
    except PlaybookNotFoundError as error:
        raise _not_found(error) from error


@router.patch("/{setup_id}")
async def update_setup(setup_id: str, payload: PlaybookSetupUpdate, service: PlaybookService = Depends(get_playbook_service)):
    try:
        return service.updateSetup(setup_id, payload)
    except PlaybookNotFoundError as error:
        raise _not_found(error) from error


@router.delete("/{setup_id}")
async def delete_setup(setup_id: str, service: PlaybookService = Depends(get_playbook_service)):
    try:
        return service.deleteSetup(setup_id)
    except PlaybookNotFoundError as error:
        raise _not_found(error) from error
