"""Beanie ODM model for vector embeddings stored in the RAG MongoDB.

Each record stores a text chunk and its embedding vector, linked to the
parent document by UUID.
"""

from datetime import datetime, timezone
from typing import List

from beanie import Document
from pydantic import Field


class EmbeddingRecord(Document):
    """A single text chunk and its embedding vector for RAG search.

    Attributes:
        document_uuid: UUID of the document this chunk belongs to.
        chunk_text: The original text that was embedded.
        embedding: The float vector produced by the embedding model.
        created_at: ISO 8601 timestamp of when the embedding was stored.
    """

    document_uuid: str = Field(index=True)
    chunk_text: str
    embedding: List[float]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Settings:
        name = "embeddings"
