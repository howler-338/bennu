# Bennu — Product Requirements Document (PRD)

## Project Overview

Bennu is an enterprise-style AI knowledge platform designed to demonstrate modern cloud-native architecture, Retrieval-Augmented Generation (RAG), vector search, asynchronous document processing, and self-hosted AI inference using Ollama.

The platform is intended to serve as:

- A flagship consulting portfolio project
- A production-style architecture showcase
- A future SaaS foundation
- A demonstration of scalable AI infrastructure design

The project emphasizes:

- AI cost optimization
- Self-hosted inference
- Privacy-first architecture
- Modular backend services
- Enterprise-ready system design
- Cloud-native deployment practices

---

# Core Objectives

## Primary Goals

### 1. Demonstrate Senior Architecture Skills
The platform should showcase:

- Distributed system thinking
- Clean service boundaries
- Async processing pipelines
- Scalable infrastructure design
- Reliability engineering concepts
- AI systems integration
- Production deployment readiness

### 2. Demonstrate AI Integration Expertise
The platform should demonstrate:

- Retrieval-Augmented Generation (RAG)
- Vector search workflows
- Embedding pipelines
- Local LLM orchestration
- Hybrid AI architecture possibilities
- Semantic document retrieval

### 3. Demonstrate Enterprise Readiness
The project should communicate:

- Scalability
- Security awareness
- Cost optimization
- Observability
- Deployment maturity
- Infrastructure automation

---

# Technology Stack

## Frontend

### Core Technologies
- React 18
- Vite
- TypeScript
- Tailwind CSS
- Zustand (auth state, persisted to localStorage)
- React Router v6

### Structure
```
frontend/
├── src/
│   ├── api/          # Typed fetch wrappers per domain
│   ├── store/        # Zustand auth store
│   ├── components/   # Shared UI components
│   ├── layouts/      # AppLayout (sidebar nav), AuthLayout
│   ├── pages/        # Login, Register, Documents, Search, Chat
│   ├── types/        # Shared TypeScript interfaces
│   └── hooks/        # Custom hooks (future)
├── index.html
└── vite.config.ts    # Proxies /api to backend in dev
```

### Future Enhancements
- React Query for server state caching
- Component library (shadcn/ui)
- Dark mode support
- Streaming chat responses

---

## Backend

### Core Technologies
- Flask 3.x
- Flask-Smorest (OpenAPI/Swagger docs, request validation)
- marshmallow (serialization and schema validation)
- Flask-SQLAlchemy + Flask-Migrate (Alembic)
- Flask-JWT-Extended
- Flask-Limiter (Redis-backed rate limiting)
- Celery 5 + Redis (async task queue)
- Gunicorn (production WSGI server, 4 workers)

### Responsibilities
- API gateway
- Authentication + RBAC
- Chat orchestration
- Document management
- RAG coordination
- Background job management
- Admin operations

---

## Database

### Primary Database
- PostgreSQL 16

### Vector Storage
- pgvector extension (768-dim vectors, cosine similarity)

### Responsibilities
- User data and roles
- Document metadata and status lifecycle
- Document chunks with embeddings
- Conversation history (future)
- Audit logs (future)

---

## AI Infrastructure

### Local Inference
- Ollama

### Models in Use
#### Embedding Model
- `nomic-embed-text` — 768-dim, fast, well-suited for RAG

#### Chat Model
- `llama3.2:3b` — 3B params, ~2GB, fast response times

### Future Enhancements
- Multi-model routing
- Hybrid local/cloud inference (OpenAI fallback)
- Larger chat models (llama3:8b, mistral:7b)

---

## Infrastructure

### Local Development
- Docker Compose (all services)
- Vite dev server (frontend, with /api proxy)

### Production (DigitalOcean VPS)
- Docker Compose on a single VPS droplet
- Gunicorn for Flask
- Separate Celery worker + Celery beat containers
- All secrets via environment variables

### Future Infrastructure
- GitHub Actions CI/CD
- Terraform for infrastructure provisioning
- Multi-droplet horizontal scaling

---

# High-Level Architecture

```
[ React Frontend (Vite / Tailwind) ]
        |
        v (served from Flask on port 8000)
[ Flask API Gateway (Gunicorn) ]
        |
        ├── /api/auth       → JWT auth (register, login, refresh, me)
        ├── /api/documents  → Upload, list, get, delete
        ├── /api/search     → Semantic vector search
        ├── /api/chat       → RAG chat with context injection
        └── /api/admin      → Admin dashboard (RBAC)
                |
                ├── PostgreSQL + pgvector  (documents, chunks, embeddings)
                ├── Redis                  (Celery broker + rate limiter)
                └── Celery Workers
                        |
                        ├── process_document  → extract → chunk → embed → store
                        └── retry_stuck_documents (beat, every 5 min)
                                |
                                └── Ollama
                                        ├── nomic-embed-text  (embeddings)
                                        └── llama3.2:3b       (chat generation)
```

---

# Product Features

# MVP Scope

The MVP prioritizes architecture quality and backend workflows over UI complexity.

---

## Feature 1 — Authentication ✅ Complete

### Requirements
Users should be able to:

- Register ✅
- Login ✅
- Logout ✅
- Maintain sessions ✅

### Implementation Notes
- JWT-based auth using Flask-JWT-Extended
- Access token + refresh token pattern
- Password hashing via Werkzeug
- Protected routes via `@jwt_required()` decorator
- Role field on users: `USER` | `ADMIN`
- Endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/refresh`
- Rate limited: 5/min on register, 10/min on login

### Future Enhancements
- OAuth / SSO
- Multi-factor authentication
- Enterprise identity providers

---

## Feature 2 — Document Upload ✅ Complete

### Requirements
Users should be able to:

- Upload PDFs ✅
- Upload text documents ✅
- View uploaded documents ✅
- Delete documents ✅

### Implementation Notes
- File types supported: PDF, TXT, DOCX
- Max file size: 50MB
- Files stored in Docker volume (`uploads_data`)
- Document status lifecycle: `pending → processing → ready → failed`
- Endpoints: `POST /api/documents`, `GET /api/documents`, `GET /api/documents/<id>`, `DELETE /api/documents/<id>`
- All routes JWT-protected and user-scoped
- Upload rate limited: 20/min

---

## Feature 3 — Document Processing Pipeline ✅ Complete

### Requirements
Uploaded documents should:

1. Be parsed ✅
2. Be chunked ✅
3. Generate embeddings ✅
4. Store vectors in pgvector ✅
5. Become searchable ✅

### Implementation Notes
- Async processing via Celery worker triggered immediately on upload
- Text extraction: `pypdf` (PDF), `python-docx` (DOCX), plain read (TXT)
- Chunking: 1000-char chunks with 200-char overlap
- Embeddings: `nomic-embed-text` via Ollama `/api/embeddings` (768 dimensions)
- Vectors stored in `document_chunks` table with pgvector `Vector(768)` column
- Retry: up to 3 attempts with exponential backoff; marks `FAILED` on exhaustion
- Celery beat retries documents stuck in `PROCESSING` for >10 min (every 5 min)

---

## Feature 4 — Semantic Search ✅ Complete

### Requirements
Users should be able to:

- Search documents semantically ✅
- Retrieve relevant chunks ✅
- View similarity scores ✅

### Implementation Notes
- `POST /api/search` — accepts `query` string and optional `limit` (default 5)
- Query is embedded with `nomic-embed-text` via Ollama
- pgvector cosine distance search over user-scoped chunks
- Results include: chunk content, similarity score (0–1), source document metadata
- JWT-protected and scoped to authenticated user's documents

---

## Feature 5 — RAG Chat ✅ Complete

### Requirements
Users should be able to:

- Ask questions about uploaded documents ✅
- Receive contextual answers ✅
- See source attribution ✅
- Maintain conversation history ✅

### Implementation Notes
- `POST /api/chat` — accepts `message`, optional `history` array, optional `limit`
- Embeds query → retrieves top-k chunks → injects as system context → calls `llama3.2:3b`
- System prompt instructs model to answer only from provided context
- Multi-turn history supported via `history` field (client-managed)
- Sources returned with each reply: document filename + chunk index
- Falls back to a general assistant prompt when no documents exist

### Future Enhancements
- Streaming responses
- Server-side conversation persistence
- Token budget management for long histories

---

## Feature 6 — Admin Dashboard ✅ Complete

### Requirements
Administrators should be able to:

- List all users ✅
- Activate / deactivate users ✅
- Change user roles ✅
- Delete users ✅
- View system stats (document counts by status) ✅
- View failed documents with owner info ✅
- Reprocess failed documents ✅

### Implementation Notes
- All `/api/admin/*` routes require `UserRole.ADMIN`
- `admin_required` decorator verifies JWT + role
- `flask make-admin <email>` CLI command to bootstrap first admin
- Stats endpoint aggregates document counts across all users
- Endpoints: `GET /api/admin/users`, `PATCH /api/admin/users/<id>`, `DELETE /api/admin/users/<id>`, `GET /api/admin/stats`, `GET /api/admin/documents/failed`, `POST /api/admin/documents/<id>/reprocess`

---

# AI Architecture

## Provider Approach

The platform currently uses Ollama directly via HTTP (`/api/embeddings`, `/api/chat`). The `services/embedder.py` and `services/llm.py` modules are the abstraction boundary — LLM provider details are isolated from business logic.

## Future Provider Abstraction

```python
class LLMProvider:
    def embed(self, text: str) -> list[float]: ...
    def chat(self, messages: list) -> str: ...
```

Planned providers:
- `OllamaProvider` — local inference (current)
- `OpenAIProvider` — cloud inference / failover
- `HybridProvider` — local-first with cloud fallback for cost optimization

---

# Backend Architecture

```
backend/
├── app/
│   ├── admin/        # Admin endpoints + RBAC decorator
│   ├── api/          # Health check
│   ├── auth/         # JWT auth, User model, UserRole
│   ├── chat/         # RAG chat endpoint
│   ├── documents/    # Upload, list, get, delete
│   ├── embeddings/   # DocumentChunk model + pgvector
│   ├── search/       # Semantic search endpoint
│   ├── services/     # text_extractor, chunker, embedder, llm
│   ├── workers/      # Celery app + document tasks + beat schedule
│   └── config/       # Environment-based config classes
├── migrations/       # Alembic migrations
├── tests/            # pytest suite (41 tests)
├── gunicorn.conf.py  # Production WSGI config
├── Dockerfile
└── requirements.txt
```

---

# Non-Functional Requirements

## Scalability

The architecture supports:

- Horizontal API scaling (Gunicorn workers, stateless JWT)
- Background worker scaling (additional Celery worker containers)
- Separate inference service (Ollama runs independently)
- pgvector scales with PostgreSQL

---

## Reliability

Implemented:
- Celery retry with exponential backoff (3 attempts)
- Celery beat for stuck document recovery (every 5 min)
- Document status lifecycle with explicit failure state
- Health check endpoint (`GET /api/health`)

Future:
- Queue visibility dashboard
- Dead-letter queue
- Circuit breaker for Ollama

---

## Security

Implemented:
- JWT authentication (access + refresh tokens)
- Role-based access control (`USER` / `ADMIN`)
- Redis-backed rate limiting (Flask-Limiter)
- File type and size validation
- User-scoped data access (no cross-user data leakage)
- Secrets via environment variables (`.env.example` documented)

Future:
- Virus scanning on upload
- Audit logging
- OAuth / SSO
- mTLS between services

---

## Observability

Implemented:
- Structured JSON logging (production)
- Document processing status lifecycle
- Celery task result backend (Redis)

Future:
- Prometheus metrics
- Grafana dashboards
- OpenTelemetry tracing
- Alerting on FAILED document rate

---

# Deployment Strategy

## Local Development

```bash
docker compose up -d        # Start all services
cd frontend && npm run dev  # Frontend with HMR at localhost:5173
```

Services: backend (Gunicorn), celery_worker, celery_beat, postgres, redis, ollama

---

## Production — DigitalOcean VPS

Deployment model: Docker Compose on a single droplet.

Steps:
1. Provision droplet (Ubuntu, 4GB+ RAM for Ollama)
2. Install Docker + Docker Compose
3. Clone repo, copy `.env.example` → `.env`, set real secrets
4. `cd frontend && npm run build` (build static assets)
5. `docker compose up -d`
6. `docker compose exec backend flask db upgrade`
7. `docker compose exec backend flask make-admin <email>`

All services run in containers. Frontend is served as static files by Flask/Gunicorn.

### Future
- GitHub Actions for automated builds and deploy-on-push
- Terraform for droplet provisioning
- Managed PostgreSQL (DigitalOcean) for production database

---

# Confirmed Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector storage | pgvector (PostgreSQL extension) | Reduces infrastructure complexity — no separate vector DB needed |
| API framework | Flask-Smorest | Auto-generates OpenAPI docs, marshmallow validation, clean blueprint structure |
| Auth strategy | JWT (access + refresh tokens) | Stateless, scalable, enterprise-standard |
| Local dev | Docker Compose | Zero-setup, consistent across machines, close to production |
| Embedding model | `nomic-embed-text` (768-dim via Ollama) | Fast, well-suited for RAG, runs on CPU |
| Chat model | `llama3.2:3b` (via Ollama) | Fast on modest hardware, good quality for document Q&A |
| Frontend state | Zustand | Minimal, hook-based, no boilerplate |
| Frontend styling | Tailwind CSS | Utility-first, no component library overhead |
| WSGI server | Gunicorn (4 workers) | Production-grade, replaces Flask dev server |
| Rate limiting | Flask-Limiter + Redis | Protects auth and upload endpoints from abuse |
| Deployment target | DigitalOcean VPS (Docker Compose) | Simple, cost-effective, avoids Kubernetes complexity |

---

# Testing

## Coverage
- 41 tests, all passing
- Unit tests: `chunker`, `text_extractor`, `embedder` (mocked Ollama)
- Integration tests: auth, documents, admin (real PostgreSQL test DB)
- Celery tasks mocked in tests (no Redis dependency)

## Running Tests
```bash
docker compose exec backend pytest -v
```

---

# Long-Term Vision

Bennu should eventually evolve into:

- A consulting showcase platform
- A reusable enterprise AI starter platform
- A SaaS AI knowledge product
- A hybrid AI infrastructure demo
- A lead-generation asset for consulting services

---

# Future Enhancements

## AI Enhancements
- Multi-model routing
- Hybrid local/cloud inference
- Agent workflows with tool calling
- Long-term memory / conversation persistence
- Streaming chat responses

## Enterprise Enhancements
- Multi-tenancy
- Audit logs
- SSO / OAuth
- Enterprise permissions

## Infrastructure Enhancements
- GitHub Actions CI/CD
- Terraform for DigitalOcean provisioning
- Managed PostgreSQL
- S3-compatible object storage for uploaded files
- Monitoring stack (Prometheus + Grafana)

---

# Repository

## Visibility
Public — portfolio showcase

## License
None initially, to preserve SaaS and commercialization flexibility.

## GitHub Description
> Enterprise AI knowledge platform using RAG, vector search, and self-hosted LLM inference with Ollama.

---

# Key Portfolio Messaging

This project communicates:

- Senior engineering capability
- Enterprise architecture thinking
- AI systems expertise (RAG, embeddings, vector search)
- Production deployment maturity (Gunicorn, rate limiting, structured logging)
- Cost optimization (self-hosted inference, no cloud AI spend)
- Cloud-native engineering practices
- Consulting-level communication and documentation
