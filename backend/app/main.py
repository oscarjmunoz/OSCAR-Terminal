# backend/app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import build_health_payload
from app.api.router import api_router

from app.config.settings import settings
from app.core.logger import logger

from app.database.base import Base
from app.database.session import engine

import app.models
import app.market.models
import app.smart_money

logger.info("Starting OSCAR Terminal...")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Backend started successfully.")
    try:
        yield
    finally:
        logger.info("Backend stopped.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():

    return {

        "application": settings.APP_NAME,

        "version": settings.APP_VERSION,

        "status": "running",

    }


@app.get("/health")
async def root_health():
    return build_health_payload()