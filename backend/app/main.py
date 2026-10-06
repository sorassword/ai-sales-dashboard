"""
FastAPI entrypoint.

Run locally:  uvicorn app.main:app --reload --port 8000
Docs:         http://localhost:8000/docs   (auto-generated OpenAPI)

The chatbot lives elsewhere for now — when you add it, drop a new router
(e.g. app/api/routes_chat.py) and mount it below. Nothing else changes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_data, routes_overview
from app.config import settings

app = FastAPI(
    title="AI Sales Assistant — Dashboard API",
    description="Mock backend for the analytics & gamification dashboard demo.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_overview.router)
app.include_router(routes_data.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "AI Sales Assistant Dashboard API",
        "status": "ok",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok", "mode": "mock"}
