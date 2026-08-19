"""RAG (retrieval-augmented generation) endpoints for vector indexing and search.

Routes are prefixed with ``/api/rag``. The index endpoint splits document
text into chunks and stores their embedding vectors. The search endpoint
embeds a query and returns the most similar chunks by cosine similarity.
"""

import math
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.embedding import EmbeddingRecord
from app.services.embedding import generate_embedding, generate_embeddings

router = APIRouter(prefix="/api/rag", tags=["rag"])


class IndexRequest(BaseModel):
    """Request body for the index endpoint.

    Attributes:
        document_uuid: UUID of the document being indexed.
        texts: List of text chunks to embed and store.
    """

    document_uuid: str
    texts: List[str]


class SearchRequest(BaseModel):
    """Request body for the search endpoint.

    Attributes:
        query: The natural-language query string to search for.
        top_k: Maximum number of results to return. Defaults to 5.
    """

    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """A single search result item.

    Attributes:
        document_uuid: UUID of the document the chunk belongs to.
        chunk_text: The original text of the matched chunk.
        score: Cosine similarity score (higher is better).
    """

    document_uuid: str
    chunk_text: str
    score: float


@router.post("/index")
async def index_document(req: IndexRequest):
    """Index document text chunks by generating and storing their embeddings.

    Args:
        req: The index request containing a document UUID and text chunks.

    Raises:
        HTTPException: 400 if the texts list is empty.

    Returns:
        A dict with the count of indexed chunks: ``{"indexed": N}``.
    """
    if not req.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    embeddings = generate_embeddings(req.texts)
    for text, emb in zip(req.texts, embeddings):
        record = EmbeddingRecord(
            document_uuid=req.document_uuid,
            chunk_text=text,
            embedding=emb,
        )
        await record.insert()
    return {"indexed": len(req.texts)}


@router.post("/search", response_model=List[SearchResult])
async def search(req: SearchRequest):
    """Semantic search across all indexed document chunks.

    Embeds the query, computes cosine similarity against every stored
    embedding, and returns the top-k results sorted by score descending.

    Args:
        req: The search request containing a query and optional top_k.

    Returns:
        A list of search results, highest similarity first.
    """
    query_embedding = generate_embedding(req.query)
    all_embeddings = await EmbeddingRecord.find_all().to_list()
    if not all_embeddings:
        return []
    results = []
    for record in all_embeddings:
        score = cosine_similarity(query_embedding, record.embedding)
        results.append(
            SearchResult(
                document_uuid=record.document_uuid,
                chunk_text=record.chunk_text,
                score=score,
            )
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results[: req.top_k]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute the cosine similarity between two vectors.

    Returns a value in the range [-1, 1], or 0.0 if either vector has
    zero magnitude (to avoid division by zero).

    Args:
        a: The first vector.
        b: The second vector.

    Returns:
        The cosine similarity score.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
