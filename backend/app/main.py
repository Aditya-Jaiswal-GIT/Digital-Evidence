
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

        print("Application startup successful!")

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

# CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
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
