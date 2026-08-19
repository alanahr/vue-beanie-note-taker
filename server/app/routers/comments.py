"""CRUD endpoints for inline comments.

Comment routes are prefixed with ``/api``. Comments belong to a specific
document (identified by UUID) and carry an optional character-offset range
that records the text selection the comment applies to.
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.comment import CommentRange, CommentRecord

router = APIRouter(prefix="/api", tags=["comments"])


class CommentBody(BaseModel):
    """Request body for creating a comment.

    Attributes:
        comment: The comment body text. Required.
        user: The author of the comment. Required.
        text: The highlighted text that was commented on. Defaults to empty.
        closed: Whether the comment is resolved. Defaults to False.
        range: Optional character-offset range of the commented selection.
    """

    comment: str
    user: str
    text: str = ""
    closed: bool = False
    range: Optional[CommentRange] = None


class CommentUpdateBody(BaseModel):
    """Request body for partially updating a comment.

    All fields are optional; only provided fields are applied.

    Attributes:
        comment: New comment body text.
        closed: New resolved status.
        range: New character-offset range.
    """

    comment: Optional[str] = None
    closed: Optional[bool] = None
    range: Optional[CommentRange] = None


class CommentResponse(BaseModel):
    """Response model for comment operations.

    Attributes:
        id: The comment's unique identifier.
        document_uuid: UUID of the document this comment belongs to.
        text: The highlighted text that was commented on.
        comment: The comment body text.
        user: The author of the comment.
        created_at: ISO 8601 timestamp of creation.
        closed: Whether the comment has been resolved/closed.
        range: Optional character-offset range of the commented selection.
    """

    id: str
    document_uuid: str
    text: str
    comment: str
    user: str
    created_at: str
    closed: bool
    range: Optional[CommentRange] = None


def to_response(rec: CommentRecord) -> CommentResponse:
    """Convert a ``CommentRecord`` to a ``CommentResponse``.

    Maps the internal ``comment_id`` field to the external ``id`` field
    so the API exposes a clean identifier name.

    Args:
        rec: The Beanie comment record to convert.

    Returns:
        A ``CommentResponse`` suitable for JSON serialisation.
    """
    return CommentResponse(
        id=rec.comment_id,
        document_uuid=rec.document_uuid,
        text=rec.text,
        comment=rec.comment,
        user=rec.user,
        created_at=rec.created_at,
        closed=rec.closed,
        range=rec.range,
    )


@router.get("/documents/{doc_uuid}/comments", response_model=List[CommentResponse])
async def list_comments(doc_uuid: str):
    """List all comments for a given document.

    Args:
        doc_uuid: The UUID of the document whose comments to retrieve.

    Returns:
        A list of comment response objects (possibly empty).
    """
    comments = await CommentRecord.find(
        CommentRecord.document_uuid == doc_uuid
    ).to_list()
    return [to_response(c) for c in comments]


@router.post("/documents/{doc_uuid}/comments", response_model=CommentResponse)
async def create_comment(doc_uuid: str, body: CommentBody):
    """Create a new comment on a document.

    Generates a new UUID for the comment and stores it linked to the
    given document UUID.

    Args:
        doc_uuid: The UUID of the document to comment on.
        body: The comment body with text, author, and optional range.

    Returns:
        The newly created comment as a response object.
    """
    import uuid as uuid_lib

    rec = CommentRecord(
        comment_id=str(uuid_lib.uuid4()),
        document_uuid=doc_uuid,
        text=body.text,
        comment=body.comment,
        user=body.user,
        created_at=datetime.now(timezone.utc).isoformat(),
        closed=body.closed,
        range=body.range,
    )
    await rec.insert()
    return to_response(rec)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: str, body: CommentUpdateBody):
    """Partially update a comment by its ID.

    Only fields provided in the request body are applied; omitted fields
    retain their existing values.

    Args:
        comment_id: The unique identifier of the comment to update.
        body: The fields to update.

    Raises:
        HTTPException: 404 if no comment exists with the given ID.

    Returns:
        The updated comment as a response object.
    """
    rec = await CommentRecord.find_one(CommentRecord.comment_id == comment_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Comment not found")
    if body.comment is not None:
        rec.comment = body.comment
    if body.closed is not None:
        rec.closed = body.closed
    if body.range is not None:
        rec.range = body.range
    await rec.save()
    return to_response(rec)


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    """Delete a comment by its ID.

    Args:
        comment_id: The unique identifier of the comment to delete.

    Raises:
        HTTPException: 404 if no comment exists with the given ID.

    Returns:
        A dict confirming deletion: ``{"deleted": True}``.
    """
    rec = await CommentRecord.find_one(CommentRecord.comment_id == comment_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Comment not found")
    await rec.delete()
    return {"deleted": True}
