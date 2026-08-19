"""Beanie ODM model for documents stored in the primary MongoDB.

The ``content`` field stores the full Tiptap JSON document structure.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from beanie import Document
from pydantic import Field


class DocumentRecord(Document):
    """A single Tiptap document record.

    Attributes:
        uuid: Unique identifier used by the front-end to load/save documents.
        content: The full Tiptap JSON document tree.
        updated_at: ISO 8601 timestamp of the last save.
    """

    uuid: str = Field(index=True, unique=True)
    content: Dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Settings:
        name = "documents"
