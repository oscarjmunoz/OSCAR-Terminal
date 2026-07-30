from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "OSCAR Terminal",
        "version": "0.1.0-alpha",
    }