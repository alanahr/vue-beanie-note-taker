import pytest
from pydantic import ValidationError

from app.models.comment import CommentRange
from app.routers.comments import CommentBody, CommentResponse, to_response
from app.routers.rag import cosine_similarity


# ---------------------------------------------------------------------------
# cosine_similarity
# ---------------------------------------------------------------------------

def test_cosine_similarity_identical_vectors():
    vec = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    a = [0.0, 0.0]
    b = [1.0, 1.0]
    assert cosine_similarity(a, b) == 0.0


def test_cosine_similarity_partial_overlap():
    a = [1.0, 0.0]
    b = [1.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.7071, rel=1e-3)


# ---------------------------------------------------------------------------
# to_response
# ---------------------------------------------------------------------------

def test_to_response_maps_fields():
    from app.models.comment import CommentRecord

    rec = CommentRecord(
        comment_id="abc-123",
        document_uuid="doc-1",
        text="highlighted text",
        comment="fix this",
        user="alice",
        created_at="2026-01-01T00:00:00Z",
        closed=False,
        range=CommentRange(**{"from": 0, "to": 10}),
    )
    resp = to_response(rec)
    assert isinstance(resp, CommentResponse)
    assert resp.id == "abc-123"
    assert resp.document_uuid == "doc-1"
    assert resp.text == "highlighted text"
    assert resp.comment == "fix this"
    assert resp.user == "alice"
    assert resp.created_at == "2026-01-01T00:00:00Z"
    assert resp.closed is False
    assert resp.range is not None
    assert resp.range.from_ == 0
    assert resp.range.to == 10


def test_to_response_handles_null_range():
    from app.models.comment import CommentRecord

    rec = CommentRecord(
        comment_id="abc-456",
        document_uuid="doc-2",
        text="",
        comment="note",
        user="bob",
        created_at="2026-01-01T00:00:00Z",
        closed=True,
        range=None,
    )
    resp = to_response(rec)
    assert resp.range is None
    assert resp.closed is True


# ---------------------------------------------------------------------------
# Pydantic model validation
# ---------------------------------------------------------------------------

def test_comment_body_valid():
    body = CommentBody(comment="hello", user="alice")
    assert body.comment == "hello"
    assert body.user == "alice"
    assert body.text == ""
    assert body.closed is False
    assert body.range is None


def test_comment_body_missing_required_comment():
    with pytest.raises(ValidationError):
        CommentBody(user="alice")


def test_comment_body_missing_required_user():
    with pytest.raises(ValidationError):
        CommentBody(comment="hello")


def test_comment_range_valid():
    r = CommentRange(**{"from": 5, "to": 15})
    assert r.from_ == 5
    assert r.to == 15


def test_comment_range_missing_from():
    with pytest.raises(ValidationError):
        CommentRange(**{"to": 15})


def test_document_body_valid():
    from app.routers.documents import DocumentBody

    body = DocumentBody(uuid="doc-1", content={"type": "doc", "content": []})
    assert body.uuid == "doc-1"
    assert body.content == {"type": "doc", "content": []}
    assert body.updated_at is None


def test_document_body_missing_required_uuid():
    from app.routers.documents import DocumentBody

    with pytest.raises(ValidationError):
        DocumentBody(content={"type": "doc"})
