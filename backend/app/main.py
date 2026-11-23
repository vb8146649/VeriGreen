"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import audit, claims, health


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db(settings.DATABASE_URL)
    yield


app = FastAPI(title="VeriGreen AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(audit.router)
app.include_router(claims.router)
