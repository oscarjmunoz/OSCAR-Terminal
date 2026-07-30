from fastapi import FastAPI

from app.api.router import api_router
from app.config.settings import settings
from app.core.logger import logger

logger.info("Starting OSCAR Terminal...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Backend started successfully.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Backend stopped.")


@app.get("/")
async def root():
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }