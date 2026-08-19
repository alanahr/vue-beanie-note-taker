import pytest

from app.models.document import DocumentRecord

pytestmark = pytest.mark.asyncio


async def test_list_documents(client, seed_db):
    resp = await client.get("/api/documents")
    assert resp.status_code == 200
    uuids = resp.json()
    assert "test-doc-0001" in uuids
    assert "test-doc-0002" in uuids
    assert "test-doc-0003" in uuids
    assert len(uuids) == 3


async def test_get_document_found(client, seed_db):
    resp = await client.get("/api/documents/test-doc-0001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["uuid"] == "test-doc-0001"
    assert body["content"]["type"] == "doc"
    assert body["updated_at"] == "2026-08-18T00:00:00.000Z"


async def test_get_document_not_found(client, seed_db):
    resp = await client.get("/api/documents/nonexistent")
    assert resp.status_code == 404


async def test_save_document_creates_new(client, seed_db):
    payload = {
        "uuid": "test-doc-new",
        "content": {"type": "doc", "content": [{"type": "paragraph"}]},
    }
    resp = await client.put("/api/documents", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["uuid"] == "test-doc-new"
    assert body["updated_at"] != ""

    # Confirm it persists
    resp2 = await client.get("/api/documents/test-doc-new")
    assert resp2.status_code == 200
    assert resp2.json()["uuid"] == "test-doc-new"


async def test_save_document_updates_existing(client, seed_db):
    payload = {
        "uuid": "test-doc-0001",
        "content": {"type": "doc", "content": [{"type": "paragraph"}]},
    }
    resp = await client.put("/api/documents", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["uuid"] == "test-doc-0001"
    assert body["updated_at"] != "2026-08-18T00:00:00.000Z"


async def test_delete_document_found(client, seed_db):
    resp = await client.delete("/api/documents/test-doc-0002")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    # Confirm it's gone
    resp2 = await client.get("/api/documents/test-doc-0002")
    assert resp2.status_code == 404


async def test_delete_document_not_found(client, seed_db):
    resp = await client.delete("/api/documents/nonexistent")
    assert resp.status_code == 404
