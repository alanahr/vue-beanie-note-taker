"""FastAPI application factory and router registration.

Creates the FastAPI app, configures CORS middleware from the ``cors_origins``
setting, and registers the document, RAG, and comment routers. A lifespan
handler initialises both MongoDB connections on startup.
"""
from datetime import datetime

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, init_rag_db
from app.routers import comments, documents, rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise both MongoDB connections on startup, close on shutdown."""
    await init_db()
    await init_rag_db()
    yield

app = FastAPI(title="Tiptap Editor API", lifespan=lifespan)

# Parse the comma-separated CORS origins from settings.
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(comments.router)


@app.get("/health")
async def health():
    """Return a simple health-check payload for uptime monitoring."""
    return {"status": "ok"}
