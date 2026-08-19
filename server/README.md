# Server — FastAPI + Beanie Back-end

The back-end for the Tiptap rich text editor. Built with FastAPI, Uvicorn, and Beanie (an async MongoDB ODM). It manages document storage, inline comments, and RAG (retrieval-augmented generation) vector search across two MongoDB databases.

## Project Structure

```
server/
├── Dockerfile              # Python 3.11 Slim, installs deps, runs Uvicorn
├── .dockerignore
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Test dependencies (pytest, pytest-asyncio, httpx)
├── pytest.ini              # Pytest configuration (asyncio auto mode)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # MongoDB connection, seed data, ASGI client fixtures
│   ├── test_sync_functions.py  # Pure-function tests (no database needed)
│   ├── test_documents.py       # Document endpoint tests (async)
│   ├── test_comments.py        # Comment endpoint tests (async)
│   └── test_rag.py             # RAG search/index + health endpoint tests (async)
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI app — CORS, lifespan DB init, routers
    ├── config.py           # Pydantic Settings — reads from env file
    ├── database.py         # Motor + Beanie init for both MongoDBs
    ├── models/
    │   ├── __init__.py
    │   ├── document.py     # DocumentRecord Beanie model
    │   ├── comment.py      # CommentRecord + CommentRange Beanie model
    │   └── embedding.py    # EmbeddingRecord Beanie model (RAG)
    ├── routers/
    │   ├── __init__.py
    │   ├── documents.py    # CRUD endpoints: GET/PUT/DELETE/LIST
    │   ├── comments.py     # Comment CRUD endpoints
    │   └── rag.py           # Vector index + semantic search endpoints
    └── services/
        ├── __init__.py
        └── embedding.py    # sentence-transformers + mdbr-leaf-ir model
```

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Both MongoDB instances must be running and reachable. Update the connection strings in `env/server.env` (or set the environment variables directly) to point to your local MongoDB instances.

## API Endpoints

### Documents

| Method   | Endpoint                  | Description                        |
| -------- | ------------------------- | ---------------------------------- |
| `GET`    | `/api/documents`          | List all document UUIDs            |
| `GET`    | `/api/documents/{uuid}`   | Fetch a document by UUID           |
| `PUT`    | `/api/documents`          | Create or update a document        |
| `DELETE` | `/api/documents/{uuid}`   | Delete a document                  |

### Comments

| Method   | Endpoint                              | Description                          |
| -------- | ------------------------------------- | ------------------------------------ |
| `GET`    | `/api/documents/{doc_uuid}/comments`  | List all comments for a document     |
| `POST`   | `/api/documents/{doc_uuid}/comments`  | Create a new comment on a document   |
| `PATCH`  | `/api/comments/{comment_id}`          | Update a comment's text or status    |
| `DELETE` | `/api/comments/{comment_id}`          | Delete a comment                     |

### RAG (Vector Search)

| Method | Endpoint          | Description                                      |
| ------ | ----------------- | ------------------------------------------------ |
| `POST` | `/api/rag/index`  | Index document text chunks with embeddings       |
| `POST` | `/api/rag/search` | Semantic search across indexed documents         |

### Health

| Method | Endpoint  | Description              |
| ------ | --------- | ------------------------ |
| `GET`  | `/health` | Returns `{"status":"ok"}` |

## Tests

The server test suite uses [pytest](https://docs.pytest.org/) with [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) and [httpx](https://www.python-httpx.org/) for async endpoint testing.

### Prerequisites

Both MongoDB instances must be running and reachable on `localhost:27017` (data) and `localhost:27018` (RAG). The fastest way to start them is with the test compose file:

```bash
docker compose -f docker-compose.test.yml up -d mongo-data mongo-rag
```

### Install test dependencies and run

```bash
pip install -r requirements-dev.txt
pytest
```

### What is covered

| File | Type | What it covers |
| ---- | ---- | -------------- |
| `test_sync_functions.py` | Sync | `cosine_similarity` math, `to_response` mapping, Pydantic model validation |
| `test_documents.py` | Async | Document list, get, create, update, delete endpoints (incl. 404 cases) |
| `test_comments.py` | Async | Comment list, create, update, delete endpoints (incl. empty-list and 404 cases) |
| `test_rag.py` | Async | Health check, RAG search ranking, RAG indexing, empty-texts validation (embedding model mocked) |

### How it works

- `conftest.py` sets environment variables to point at the local test MongoDB instances, initializes Beanie for the session, and provides two fixtures:
  - `seed_db` — clears all collections and re-inserts the same seed data as `mongo-init/test-mongo-init.js` before each test
  - `client` — an `httpx.AsyncClient` wired directly to the FastAPI app via ASGI transport (no network needed)
- Synchronous tests (pure functions, model validation) run without the database
- Asynchronous tests (endpoint tests) use the `seed_db` and `client` fixtures
- The RAG embedding model is mocked in tests to avoid downloading a Hugging Face model
