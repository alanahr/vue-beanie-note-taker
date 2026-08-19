from unittest.mock import patch

import pytest

pytestmark = pytest.mark.asyncio


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_rag_search_returns_results(client, seed_db):
    fake_vector = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    with patch(
        "app.routers.rag.generate_embedding", return_value=fake_vector
    ):
        resp = await client.post("/api/rag/search", json={"query": "test", "top_k": 3})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 3
    # Results should be sorted by score descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    # The first result should be the exact-match embedding (identical vector)
    assert results[0]["document_uuid"] == "test-doc-0001"
    assert results[0]["chunk_text"] == "Test Document Heading"


async def test_rag_search_respects_top_k(client, seed_db):
    fake_vector = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    with patch(
        "app.routers.rag.generate_embedding", return_value=fake_vector
    ):
        resp = await client.post("/api/rag/search", json={"query": "test", "top_k": 1})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1


async def test_rag_index_inserts_records(client, seed_db):
    fake_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    with patch(
        "app.routers.rag.generate_embeddings", return_value=fake_embeddings
    ):
        resp = await client.post(
            "/api/rag/index",
            json={
                "document_uuid": "test-doc-new",
                "texts": ["first chunk", "second chunk"],
            },
        )
    assert resp.status_code == 200
    assert resp.json() == {"indexed": 2}

    # Confirm the records were inserted
    from app.models.embedding import EmbeddingRecord

    records = await EmbeddingRecord.find(
        EmbeddingRecord.document_uuid == "test-doc-new"
    ).to_list()
    assert len(records) == 2
    assert records[0].chunk_text == "first chunk"
    assert records[1].chunk_text == "second chunk"


async def test_rag_index_rejects_empty_texts(client, seed_db):
    resp = await client.post(
        "/api/rag/index",
        json={"document_uuid": "test-doc-new", "texts": []},
    )
    assert resp.status_code == 400
