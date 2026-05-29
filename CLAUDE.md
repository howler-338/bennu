Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
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
