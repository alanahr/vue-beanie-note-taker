"""Beanie ODM models for inline comments stored in the primary MongoDB.

Comments are linked to a document by UUID and carry an optional ``range``
that records the text selection the comment applies to.
"""

from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class CommentRange(BaseModel):
    """A character-offset range identifying the commented text selection.

    Attributes:
        from_: Start offset (aliased from ``from`` in the JSON payload).
        to: End offset.
    """

    from_: int = Field(alias="from")
    to: int

    model_config = {"populate_by_name": True}


class CommentRecord(Document):
    """A single inline comment on a document.

    Attributes:
        comment_id: Unique identifier for the comment.
        document_uuid: UUID of the document this comment belongs to.
        text: The highlighted text that was commented on.
        comment: The comment body text.
        user: The author of the comment.
        created_at: ISO 8601 timestamp of creation.
        closed: Whether the comment has been resolved/closed.
        range: Optional character-offset range of the commented selection.
    """

    comment_id: str = Field(index=True, unique=True)
    document_uuid: str = Field(index=True)
    text: str = ""
    comment: str
    user: str
    created_at: str
    closed: bool = False
    range: Optional[CommentRange] = None

    class Settings:
        name = "comments"
