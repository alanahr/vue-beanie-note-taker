"""CRUD endpoints for Tiptap documents.

All routes are prefixed with ``/api/documents``. Documents are stored as
full Tiptap JSON trees and identified by a client-generated UUID.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.document import DocumentRecord

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentBody(BaseModel):
    """Request body for creating or updating a document.

    Attributes:
        uuid: The document's unique identifier.
        content: The full Tiptap JSON document tree.
        updated_at: Optional timestamp; set automatically if omitted.
    """

    uuid: str
    content: Any
    updated_at: Optional[str] = None


class DocumentResponse(BaseModel):
    """Response model returned after get, create, or update operations.

    Attributes:
        uuid: The document's unique identifier.
        content: The full Tiptap JSON document tree.
        updated_at: ISO 8601 timestamp of the last save.
    """

    uuid: str
    content: Any
    updated_at: str


@router.get("/{doc_uuid}", response_model=DocumentResponse)
async def get_document(doc_uuid: str):
    """Fetch a single document by its UUID.

    Args:
        doc_uuid: The UUID of the document to retrieve.

    Raises:
        HTTPException: 404 if no document exists with the given UUID.

    Returns:
        The document's content and metadata.
    """
    doc = await DocumentRecord.find_one(DocumentRecord.uuid == doc_uuid)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        uuid=doc.uuid, content=doc.content, updated_at=doc.updated_at
    )


@router.put("", response_model=DocumentResponse)
async def save_document(body: DocumentBody):
    """Create a new document or update an existing one by UUID.

    If a document with the given UUID already exists, its content and
    ``updated_at`` timestamp are overwritten. Otherwise a new record is
    inserted.

    Args:
        body: The document body containing UUID and content.

    Returns:
        The saved document with its updated timestamp.
    """
    existing = await DocumentRecord.find_one(DocumentRecord.uuid == body.uuid)
    now = datetime.now(timezone.utc).isoformat()
    if existing:
        existing.content = body.content
        existing.updated_at = now
        await existing.save()
        return DocumentResponse(uuid=existing.uuid, content=existing.content, updated_at=existing.updated_at)
    doc = DocumentRecord(uuid=body.uuid, content=body.content, updated_at=now)
    await doc.insert()
    return DocumentResponse(uuid=doc.uuid, content=doc.content, updated_at=doc.updated_at)


@router.delete("/{doc_uuid}")
async def delete_document(doc_uuid: str):
    """Delete a document by its UUID.

    Args:
        doc_uuid: The UUID of the document to delete.

    Raises:
        HTTPException: 404 if no document exists with the given UUID.

    Returns:
        A dict confirming deletion: ``{"deleted": True}``.
    """
    doc = await DocumentRecord.find_one(DocumentRecord.uuid == doc_uuid)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await doc.delete()
    return {"deleted": True}


@router.get("", response_model=List[str])
async def list_documents():
    """List the UUIDs of all stored documents.

    Returns:
        A list of document UUID strings.
    """
    docs = await DocumentRecord.find_all().to_list()
    return [d.uuid for d in docs]
