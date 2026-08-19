"""MongoDB connection initialisation via Beanie.

Provides two initialisation functions — one for the primary data database
(documents and comments) and one for the RAG database (vector embeddings).
Both return the Motor client so callers can close the connection on shutdown.
"""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.comment import CommentRecord
from app.models.document import DocumentRecord
from app.models.embedding import EmbeddingRecord


async def init_db() -> AsyncIOMotorClient:
    """Initialise the primary data MongoDB and register Beanie models.

    Connects to the data MongoDB using ``settings.mongo_data_url`` and
    initialises Beanie with ``DocumentRecord`` and ``CommentRecord`` on the
    database named by ``settings.mongo_data_db``.

    Returns:
        The Motor async client for the data MongoDB.
    """
    client = AsyncIOMotorClient(settings.mongo_data_url)
    await init_beanie(
        database=client[settings.mongo_data_db],
        document_models=[DocumentRecord, CommentRecord],
    )
    return client


async def init_rag_db() -> AsyncIOMotorClient:
    """Initialise the RAG MongoDB and register the embedding model.

    Connects to the RAG MongoDB using ``settings.mongo_rag_url`` and
    initialises Beanie with ``EmbeddingRecord`` on the database named by
    ``settings.mongo_rag_db``.

    Returns:
        The Motor async client for the RAG MongoDB.
    """
    client = AsyncIOMotorClient(settings.mongo_rag_url)
    await init_beanie(
        database=client[settings.mongo_rag_db],
        document_models=[EmbeddingRecord],
    )
    return client
