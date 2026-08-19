# Tiptap Rich Text Editor — Multi-Container App

A rich text editor built with [Tiptap v3](https://tiptap.dev), Vue 3, TypeScript, and Vuetify, backed by a FastAPI + Beanie Python API and two MongoDB databases — one for document storage and one for RAG (retrieval-augmented generation) vector search.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Client    │────▶│   Server    │────▶│  mongo-data  │  Document storage
│  (Vue/Vite) │     │ (FastAPI)   │     └──────────────┘
└─────────────┘     └──────┬──────┘     ┌──────────────┐
                           └───────────▶│  mongo-rag   │  Vector search / RAG
                                        └──────────────┘
```

| Container    | Image                              | Purpose                          | Port  |
| ------------ | ---------------------------------- | -------------------------------- | ----- |
| `client`     | Node 20 Alpine (Vite preview)      | Vue 3 + Vuetify front-end        | 5173  |
| `server`     | Python 3.11 Slim (FastAPI/Uvicorn) | REST API + Beanie ODM            | 8002  |
| `mongo-data`  | mongodb-community-server           | Primary document storage         | 27017 |
| `mongo-rag`   | mongodb-community-search           | Vector embeddings for RAG        | 27018 |

## Project Structure

```
.
├── docker-compose.yml          # Orchestrates all four containers
├── docker-compose.test.yml     # Orchestrates the full stack + Cypress E2E runner
├── mongo-init/
│   └── test-mongo-init.js      # Seeds both MongoDB instances on first container init
├── env/                        # Environment configuration files
│   ├── client.env.example      # Front-end config (port, API URL)
│   ├── server.env.example      # Back-end config (Mongo URLs, ports, model)
│   ├── mongo.env.example       # MongoDB credentials and ports
│   └── test.env.example        # Test runner config (Cypress base URL)
├── client/                     # Vue 3 front-end
│   ├── Dockerfile              # Multi-stage build: build app, serve via Vite preview
│   ├── .dockerignore
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts          # Vite + Vue + Vuetify plugins
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── public/
│   │   └── vite.svg
│   └── src/
│       ├── main.ts             # App bootstrap — Vuetify, Pinia, Vue Router
│       ├── App.vue             # Root component — document bar, save flow, previews
│       ├── style.css           # Global styles and CSS variables
│       ├── vite-env.d.ts       # Vite type declarations
│       ├── assets/
│       │   └── vue.svg
│       ├── components/
│       │   ├── TiptapEditor.vue     # Core editor — all Tiptap extensions, auto-save
│       │   ├── EditorToolbar.vue    # Formatting toolbar
│       │   └── CommentPanel.vue     # Comment management panel
│       ├── extensions/
│       │   └── Comment.ts           # Custom Tiptap mark for inline comments
│       └── services/
│           └── documentApi.ts       # Document CRUD via FastAPI back-end
└── server/                     # Python FastAPI back-end
    ├── Dockerfile              # Python 3.11 Slim, installs deps, runs Uvicorn
    ├── .dockerignore
    ├── requirements.txt        # FastAPI, Beanie, Motor, sentence-transformers
    ├── requirements-dev.txt    # Test dependencies (pytest, pytest-asyncio, httpx)
    ├── pytest.ini              # Pytest configuration (asyncio auto mode)
    ├── tests/                  # Server-side pytest suite
    │   ├── conftest.py         # MongoDB connection, seed data, ASGI client fixtures
    │   ├── test_sync_functions.py   # Pure-function tests (cosine_similarity, validation)
    │   ├── test_documents.py        # Document endpoint tests (GET/PUT/DELETE/LIST)
    │   ├── test_comments.py         # Comment endpoint tests (GET/POST/PATCH/DELETE)
    │   └── test_rag.py              # RAG search/index + health endpoint tests
    └── app/
        ├── __init__.py
        ├── main.py             # FastAPI app — CORS, lifespan DB init, routers
        ├── config.py           # Pydantic Settings — reads from env file
        ├── database.py         # Motor + Beanie init for both MongoDBs
        ├── models/
        │   ├── __init__.py
        │   ├── document.py     # DocumentRecord Beanie model
        │   ├── comment.py     # CommentRecord + CommentRange Beanie model
        │   └── embedding.py    # EmbeddingRecord Beanie model (RAG)
        ├── routers/
        │   ├── __init__.py
        │   ├── documents.py    # CRUD endpoints: GET/PUT/DELETE/LIST
        │   ├── comments.py    # Comment CRUD endpoints
        │   └── rag.py          # Vector index + semantic search endpoints
        └── services/
            ├── __init__.py
            └── embedding.py    # sentence-transformers + mdbr-leaf-ir model
```

## Tech Stack

| Layer          | Technology                                              |
| -------------- | ------------------------------------------------------- |
| Front-end      | Vue 3 (`<script setup>` SFCs), TypeScript, Vite 7      |
| UI Framework   | Vuetify 4                                               |
| State          | Pinia                                                   |
| Routing        | Vue Router 5                                            |
| Editor Core    | Tiptap v3 (`@tiptap/vue-3`, `@tiptap/starter-kit`)      |
| Syntax Highlight | Lowlight                                              |
| Back-end       | FastAPI, Uvicorn                                        |
| ODM            | Beanie (async MongoDB ODM)                             |
| Database       | MongoDB Community Server (data), MongoDB Community Search (RAG) |
| Vector Search  | sentence-transformers + `MongoDB/mdbr-leaf-ir` embedding model |

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

### 1. Create environment files

Copy each example file in `env/` to its real counterpart and adjust values as needed:

```bash
cp env/client.env.example env/client.env
cp env/server.env.example env/server.env
cp env/mongo.env.example env/mongo.env
```

Key variables to configure:

| File             | Variable                  | Description                              |
| ---------------- | ------------------------- | ---------------------------------------- |
| `env/client.env` | `CLIENT_PORT`             | Port the front-end listens on            |
|                  | `VITE_API_BASE_URL`       | URL the front-end uses to reach the API   |
| `env/server.env` | `MONGO_DATA_URL`          | Connection string for the data MongoDB   |
|                  | `MONGO_DATA_DB`           | Database name for document storage        |
|                  | `MONGO_RAG_URL`           | Connection string for the RAG MongoDB    |
|                  | `MONGO_RAG_DB`            | Database name for vector embeddings       |
|                  | `SERVER_PORT`             | Port the API listens on                   |
|                  | `EMBEDDING_MODEL_NAME`    | Hugging Face model ID for embeddings      |
| `env/mongo.env`  | `MONGO_DATA_ROOT_USERNAME`| Data MongoDB root username               |
|                  | `MONGO_DATA_ROOT_PASSWORD`| Data MongoDB root password               |
|                  | `MONGO_DATA_PORT`         | Data MongoDB port                         |
|                  | `MONGO_RAG_ROOT_USERNAME` | RAG MongoDB root username                 |
|                  | `MONGO_RAG_ROOT_PASSWORD` | RAG MongoDB root password                 |
|                  | `MONGO_RAG_PORT`          | RAG MongoDB port                           |

> If you change MongoDB credentials in `env/mongo.env`, make sure the connection strings in `env/server.env` match (username, password, and port).

### 2. Build and start all containers

```bash
docker compose up --build
```

This starts all four services:

- **Front-end** — `http://localhost:5173`
- **API** — `http://localhost:8002`
- **Data MongoDB** — `localhost:27017`
- **RAG MongoDB** — `localhost:27018`

### 3. Verify the API is running

```bash
curl http://localhost:8002/health
# {"status":"ok"}
```

## API Endpoints

### Documents

| Method   | Endpoint                  | Description                        |
| -------- | ------------------------- | ---------------------------------- |
| `GET`    | `/api/documents`          | List all document UUIDs            |
| `GET`    | `/api/documents/{uuid}`   | Fetch a document by UUID           |
| `PUT`    | `/api/documents`          | Create or update a document         |
| `DELETE` | `/api/documents/{uuid}`   | Delete a document                  |

### RAG (Vector Search)

| Method | Endpoint          | Description                                      |
| ------ | ----------------- | ------------------------------------------------ |
| `POST` | `/api/rag/index`  | Index document text chunks with embeddings       |
| `POST` | `/api/rag/search` | Semantic search across indexed documents         |

**Index request body:**
```json
{
  "document_uuid": "abc-123",
  "texts": ["First paragraph of the document", "Second paragraph"]
}
```

**Search request body:**
```json
{
  "query": "What is this document about?",
  "top_k": 5
}
```

## Testing

The project has three layers of tests: server-side unit/integration tests (pytest), front-end unit tests (Vitest), and end-to-end tests (Cypress).

### Server Tests (pytest + pytest-asyncio)

The server test suite connects to the two MongoDB instances, seeds them with the same sample data as `mongo-init/test-mongo-init.js`, and tests both pure synchronous functions and asynchronous API endpoints.

**Prerequisites:** Both MongoDB instances must be running and reachable on `localhost:27017` (data) and `localhost:27018` (RAG). The fastest way to start them is with the test compose file:

```bash
docker compose -f docker-compose.test.yml up -d mongo-data mongo-rag
```

**Install test dependencies and run:**

```bash
cd server
pip install -r requirements-dev.txt
pytest
```

**What is covered:**

| File | Type | What it covers |
| ---- | ---- | -------------- |
| `test_sync_functions.py` | Sync | `cosine_similarity` math, `to_response` mapping, Pydantic model validation |
| `test_documents.py` | Async | Document list, get, create, update, delete endpoints (incl. 404 cases) |
| `test_comments.py` | Async | Comment list, create, update, delete endpoints (incl. empty-list and 404 cases) |
| `test_rag.py` | Async | Health check, RAG search ranking, RAG indexing, empty-texts validation (embedding model mocked) |

### Front-end Unit Tests (Vitest)

```bash
cd client
npm install
npm run test
```

### End-to-End Tests (Cypress)

See [`tests/README.md`](tests/README.md) for full details. The quick command:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from e2e
```

The MongoDB seed script (`mongo-init/test-mongo-init.js`) runs automatically when the containers initialize, giving Cypress a predictable dataset.

## Local Development (without Docker)

### Front-end

```bash
cd client
npm install
npm run dev
```

### Back-end

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Both MongoDB instances must be running and reachable. Update the connection strings in `env/server.env` (or set the environment variables directly) to point to your local MongoDB instances.

## Tiptap Extensions in Use

| Extension | Package |
| --------- | ------- |
| StarterKit | `@tiptap/starter-kit` |
| Subscript | `@tiptap/extension-subscript` |
| Superscript | `@tiptap/extension-superscript` |
| Text Style | `@tiptap/extension-text-style` |
| Audio | `@tiptap/extension-audio` |
| Task List / Task Item | `@tiptap/extension-list` |
| Table / TableRow / TableHeader / TableCell | `@tiptap/extension-table` |
| Details / DetailsSummary / DetailsContent | `@tiptap/extension-details` |
| Code Block (Lowlight) | `@tiptap/extension-code-block-lowlight` |
| Typography | `@tiptap/extension-typography` |
| Find and Replace | `@tiptap/extension-find-and-replace` |
| Node Range | `@tiptap/extension-node-range` |
| Hard Break | `@tiptap/extension-hard-break` |
| Unique ID | `@tiptap/extension-unique-id` |
| File Handler | `@tiptap/extension-file-handler` |
| Table of Contents | `@tiptap/extension-table-of-contents` |
| Comment (custom) | `src/extensions/Comment.ts` |

## Scripts (client)

- `npm run dev` — start the Vite dev server
- `npm run build` — type-check with `vue-tsc` and build for production
- `npm run preview` — preview the production build locally
