import pytest

pytestmark = pytest.mark.asyncio


async def test_list_comments_for_doc_with_comments(client, seed_db):
    resp = await client.get("/api/documents/test-doc-0003/comments")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == 1
    assert comments[0]["id"] == "comment-0001"


async def test_list_comments_for_doc_with_closed_comment(client, seed_db):
    resp = await client.get("/api/documents/test-doc-0001/comments")
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) == 1
    c = comments[0]
    assert c["id"] == "comment-0002"
    assert c["closed"] is True


async def test_list_comments_empty(client, seed_db):
    resp = await client.get("/api/documents/test-doc-0002/comments")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_comment(client, seed_db):
    payload = {
        "comment": "new comment",
        "user": "tester",
        "text": "selected text",
        "closed": False,
        "range": {"from": 0, "to": 5},
    }
    resp = await client.post("/api/documents/test-doc-0001/comments", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] != ""
    assert body["document_uuid"] == "test-doc-0001"
    assert body["comment"] == "new comment"
    assert body["user"] == "tester"
    assert body["text"] == "selected text"
    assert body["closed"] is False
    assert body["range"]["from"] == 0
    assert body["range"]["to"] == 5


async def test_update_comment_found(client, seed_db):
    payload = {"comment": "updated text", "closed": True}
    resp = await client.patch("/api/comments/comment-0001", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "comment-0001"
    assert body["comment"] == "updated text"
    assert body["closed"] is True


async def test_update_comment_not_found(client, seed_db):
    resp = await client.patch("/api/comments/nonexistent", json={"comment": "x"})
    assert resp.status_code == 404


async def test_delete_comment_found(client, seed_db):
    resp = await client.delete("/api/comments/comment-0001")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    # Confirm it's gone
    resp2 = await client.get("/api/documents/test-doc-0003/comments")
    assert resp2.status_code == 200
    assert resp2.json() == []


async def test_delete_comment_not_found(client, seed_db):
    resp = await client.delete("/api/comments/nonexistent")
    assert resp.status_code == 404
