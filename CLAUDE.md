# Bennu — Claude Code Guide

## Project Overview

Bennu is an enterprise AI knowledge platform using RAG, vector search, and self-hosted LLM inference with Ollama.

## Local Development

All services run via Docker Compose. Always use Docker for database commands.

```bash
# Start all services
docker compose up -d

# Rebuild backend after dependency changes
docker compose up -d --build backend

# Run database migrations
docker compose exec backend flask db upgrade

# Generate a new migration
docker compose exec backend flask db migrate -m "description"

# View backend logs
docker compose logs backend -f
```

## Key URLs

- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (user: bennu, password: bennu, db: bennu)
- Redis: localhost:6379
- Ollama: http://localhost:11434

## Project Structure

```
bennu/
├── backend/          # Flask API
├── frontend/         # React + Vite (coming soon)
├── infrastructure/   # Docker, Terraform, Kubernetes
├── docs/
└── screenshots/
```

## Backend Structure

```
backend/
├── app/
│   ├── api/          # Health check and shared API utilities
│   ├── auth/         # JWT authentication
│   ├── chat/         # RAG chat (coming soon)
│   ├── documents/    # Document upload and management
│   ├── embeddings/   # Embedding pipeline (coming soon)
│   ├── rag/          # RAG pipeline (coming soon)
│   ├── services/     # Shared services
│   ├── workers/      # Celery workers (coming soon)
│   └── config/       # Environment-based config
├── migrations/       # Alembic migrations
└── tests/
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values. Never commit `.env`.

## Feature Status

- Feature 1 — Authentication ✅
- Feature 2 — Document Upload ✅
- Feature 3 — Document Processing Pipeline 🔄
- Feature 4 — Semantic Search
- Feature 5 — RAG Chat
- Feature 6 — Admin Dashboard
