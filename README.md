# Bennu

Enterprise AI knowledge platform — RAG, vector search, and self-hosted LLM inference.

Upload documents. Ask questions. Get answers grounded in your content.

---

## What it does

- **Upload** PDF, DOCX, and TXT documents
- **Process** them asynchronously — text extraction, chunking, and embedding via Ollama
- **Search** semantically across your document library
- **Chat** with an LLM that answers from your documents (RAG)
- **Administer** users, monitor processing status, and reprocess failures

---

## Architecture

```
[ React + Vite + Tailwind ]
           │
           ▼  (served by Flask on port 8000)
[ Flask API  ·  Gunicorn 4 workers ]
           │
     ┌─────┼──────────────────────┐
     │     │                      │
  Auth  Documents             Admin
  JWT   Upload/Search/Chat    RBAC
           │
           ├── PostgreSQL + pgvector   ← chunks & embeddings
           ├── Redis                   ← Celery broker + rate limiter
           └── Celery Worker + Beat
                      │
                   Ollama
                ├── nomic-embed-text   (768-dim embeddings)
                └── llama3.2:3b        (chat generation)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Zustand |
| Backend | Flask 3, Flask-Smorest, Gunicorn, Celery 5 |
| Database | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis 7 |
| AI Inference | Ollama (`nomic-embed-text`, `llama3.2:3b`) |
| Auth | JWT (Flask-JWT-Extended) |
| Rate limiting | Flask-Limiter (Redis-backed) |

---

## Getting started

### Prerequisites
- Docker + Docker Compose
- Node.js 18+ (for frontend builds)

### 1. Clone and configure

```bash
git clone https://github.com/howler-338/bennu.git
cd bennu
cp .env.example .env
# Edit .env — at minimum, set SECRET_KEY and JWT_SECRET_KEY
```

### 2. Build the frontend

```bash
cd frontend && npm install && npm run build && cd ..
```

### 3. Start all services

```bash
docker compose up -d
```

### 4. Run database migrations

```bash
docker compose exec backend flask db upgrade
```

### 5. Pull AI models

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2:3b
```

### 6. Create your admin account

Register at **http://localhost:8000/register**, then promote yourself:

```bash
docker compose exec backend flask make-admin your@email.com
```

---

## Services

| Service | URL | Description |
|---|---|---|
| App | http://localhost:8000 | React frontend + Flask API |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |
| PostgreSQL | localhost:5432 | `bennu` / `bennu` |
| Redis | localhost:6379 | Broker + cache |
| Ollama | http://localhost:11434 | LLM inference |

---

## Running tests

```bash
docker compose exec backend pytest -v
```

41 tests covering services (chunker, extractor, embedder) and API endpoints (auth, documents, admin).

---

## Project structure

```
bennu/
├── backend/
│   ├── app/
│   │   ├── admin/        # Admin dashboard (RBAC)
│   │   ├── auth/         # JWT auth + user roles
│   │   ├── chat/         # RAG chat endpoint
│   │   ├── documents/    # Upload and management
│   │   ├── embeddings/   # DocumentChunk model + pgvector
│   │   ├── search/       # Semantic search
│   │   ├── services/     # text_extractor, chunker, embedder, llm
│   │   └── workers/      # Celery tasks + beat schedule
│   ├── tests/            # pytest suite
│   └── gunicorn.conf.py
├── frontend/
│   └── src/
│       ├── api/          # Typed API client
│       ├── pages/        # Login, Documents, Search, Chat
│       └── store/        # Zustand auth store
├── docker-compose.yml
└── .env.example
```

---

## Document processing pipeline

```
Upload
  │
  ▼
PENDING → Celery task dispatched
  │
  ▼
PROCESSING → extract text (pypdf / python-docx)
           → chunk (1000 chars, 200 overlap)
           → embed each chunk (nomic-embed-text via Ollama)
           → store in document_chunks (pgvector)
  │
  ▼
READY  (or FAILED after 3 retries)
```

Celery beat runs every 5 minutes and re-queues any document stuck in `PROCESSING` for more than 10 minutes.

---

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register (rate limited: 5/min) |
| POST | `/api/auth/login` | Login (rate limited: 10/min) |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Current user |
| POST | `/api/documents` | Upload document (rate limited: 20/min) |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/<id>` | Delete document |
| POST | `/api/search` | Semantic search |
| POST | `/api/chat` | RAG chat |
| GET | `/api/admin/stats` | System stats (admin) |
| GET | `/api/admin/users` | List all users (admin) |
| GET | `/api/admin/documents/failed` | Failed documents (admin) |
| POST | `/api/admin/documents/<id>/reprocess` | Reprocess failed doc (admin) |

Full interactive docs at **http://localhost:8000/docs**.

---

## Production deployment (DigitalOcean VPS)

```bash
# On the droplet:
git clone https://github.com/howler-338/bennu.git && cd bennu
cp .env.example .env && nano .env   # set real secrets + FLASK_ENV=production
cd frontend && npm install && npm run build && cd ..
docker compose up -d
docker compose exec backend flask db upgrade
docker compose exec backend flask make-admin your@email.com
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2:3b
```

---

## Future roadmap

- GitHub Actions CI/CD (test → build → deploy)
- Terraform for droplet provisioning
- Streaming chat responses
- Conversation history persistence
- Multi-model routing (local-first, cloud fallback)
- S3-compatible storage for uploaded files
- Prometheus + Grafana observability stack
