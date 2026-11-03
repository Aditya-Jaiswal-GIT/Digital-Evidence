from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import (
    connect_database,
    close_database
)

from app.core.init_db import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        connect_database()
        initialize_database()

        yield

    finally:
        close_database()
        print("Database connection closed!")


app = FastAPI(
    title="AI-Based Digital Evidence Authenticity Analyzer",
    description="Multimodal AI-powered digital forensic platform",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "project": "Digital Evidence Authenticity Analyzer",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "api": "healthy",
        "database": "connected"
    }