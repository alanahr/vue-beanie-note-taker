import os
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# Point the server config at the local test MongoDB instances before the app loads.
os.environ.setdefault("MONGO_DATA_URL", "mongodb://root:example@localhost:27017/")
os.environ.setdefault("MONGO_DATA_DB", "tiptap_editor")
os.environ.setdefault("MONGO_RAG_URL", "mongodb://root:example@localhost:27018/")
os.environ.setdefault("MONGO_RAG_DB", "tiptap_rag")
os.environ.setdefault("SERVER_HOST", "0.0.0.0")
os.environ.setdefault("SERVER_PORT", "8002")
os.environ.setdefault("EMBEDDING_MODEL_NAME", "MongoDB/mdbr-leaf-ir")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from app.database import init_db, init_rag_db
from app.main import app
from app.models.comment import CommentRange, CommentRecord
from app.models.document import DocumentRecord
from app.models.embedding import EmbeddingRecord

# ---------------------------------------------------------------------------
# Seed data — mirrors mongo-init/test-mongo-init.js so tests run against the
# same dataset the Docker init script creates.
# ---------------------------------------------------------------------------

SEED_DOCUMENTS = [
    {
        "uuid": "test-doc-0001",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Test Document Heading"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This is a test paragraph with "},
                        {"type": "text", "marks": [{"type": "bold"}], "text": "bold text"},
                        {"type": "text", "text": " and "},
                        {"type": "text", "marks": [{"type": "italic"}], "text": "italic text"},
                        {"type": "text", "text": "."},
                    ],
                },
            ],
        },
        "updated_at": "2026-08-18T00:00:00.000Z",
    },
    {
        "uuid": "test-doc-0002",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "A second document for testing list and delete endpoints.",
                        }
                    ],
                }
            ],
        },
        "updated_at": "2026-08-18T00:00:01.000Z",
    },
    {
        "uuid": "test-doc-0003",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Document with a "},
                        {
                            "type": "text",
                            "marks": [
                                {
                                    "type": "comment",
                                    "attrs": {
                                        "comment": "This needs review",
                                        "user": "admin",
                                        "createdAt": "2026-08-18T00:00:02.000Z",
                                        "closed": False,
                                        "range": {"from": 16, "to": 24},
                                    },
                                }
                            ],
                            "text": "commented",
                        },
                        {"type": "text", "text": " section."},
                    ],
                }
            ],
        },
        "updated_at": "2026-08-18T00:00:02.000Z",
    },
]

SEED_COMMENTS = [
    {
        "comment_id": "comment-0001",
        "document_uuid": "test-doc-0003",
        "text": "commented",
        "comment": "This needs review",
        "user": "admin",
        "created_at": "2026-08-18T00:00:02.000Z",
        "closed": False,
        "range": {"from": 16, "to": 24},
    },
    {
        "comment_id": "comment-0002",
        "document_uuid": "test-doc-0001",
        "text": "bold text",
        "comment": "Consider rephrasing this",
        "user": "reviewer",
        "created_at": "2026-08-18T00:00:03.000Z",
        "closed": True,
        "range": {"from": 26, "to": 35},
    },
]

SEED_EMBEDDINGS = [
    {
        "document_uuid": "test-doc-0001",
        "chunk_text": "Test Document Heading",
        "embedding": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
        "created_at": "2026-08-18T00:00:00.000Z",
    },
    {
        "document_uuid": "test-doc-0001",
        "chunk_text": "This is a test paragraph with bold text and italic text.",
        "embedding": [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09],
        "created_at": "2026-08-18T00:00:01.000Z",
    },
    {
        "document_uuid": "test-doc-0003",
        "chunk_text": "Document with a commented section.",
        "embedding": [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
        "created_at": "2026-08-18T00:00:02.000Z",
    },
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def mongo_client():
    """Initialize Beanie on the test MongoDB instances for the session."""
    data_client = await init_db()
    rag_client = await init_rag_db()
    yield data_client
    data_client.close()
    rag_client.close()


@pytest_asyncio.fixture
async def seed_db(mongo_client):
    """Clear and re-seed every collection before each test."""
    await DocumentRecord.delete_all()
    await CommentRecord.delete_all()
    await EmbeddingRecord.delete_all()

    for doc in SEED_DOCUMENTS:
        await DocumentRecord(**doc).insert()

    for com in SEED_COMMENTS:
        await CommentRecord(
            comment_id=com["comment_id"],
            document_uuid=com["document_uuid"],
            text=com["text"],
            comment=com["comment"],
            user=com["user"],
            created_at=com["created_at"],
            closed=com["closed"],
            range=CommentRange(**com["range"]),
        ).insert()

    for emb in SEED_EMBEDDINGS:
        await EmbeddingRecord(**emb).insert()

    yield


@pytest_asyncio.fixture
async def client(mongo_client):
    """ASGI client wired directly to the FastAPI app — no network needed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
