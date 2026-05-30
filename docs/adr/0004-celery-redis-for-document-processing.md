# 0004 — Use Celery + Redis for Async Document Processing

**Status:** Accepted

## Context

Document processing (text extraction → chunking → embedding → storage) is too slow for a synchronous HTTP request. Embedding a document with Ollama takes several seconds to minutes depending on document size. Blocking the upload response on this work would produce poor UX and tie up Gunicorn workers.

Options considered:

- **Celery + Redis** — Mature Python task queue with Redis as broker and result backend
- **RQ (Redis Queue)** — Simpler Redis-backed queue, less feature-rich
- **Threading / asyncio** — In-process background work, no separate worker process
- **Database polling** — Workers poll a jobs table, no queue infrastructure

## Decision

Use Celery 5 with Redis as both the broker and result backend. Document processing is dispatched as a Celery task immediately after upload. A separate `celery_worker` container runs the task. `celery_beat` runs a scheduler that retries documents stuck in `PROCESSING` for more than 10 minutes every 5 minutes.

## Consequences

**Positive:**
- Upload returns immediately with a `pending` status — the frontend polls for status updates
- Worker scales independently of the API (additional `celery_worker` containers)
- Celery's retry mechanism with exponential backoff handles transient Ollama failures
- Beat scheduler provides a self-healing safety net for stuck documents
- Redis is already required for Flask-Limiter — no additional infrastructure

**Negative:**
- Adds operational complexity: three containers (`backend`, `celery_worker`, `celery_beat`) instead of one
- Task state is stored in Redis with a TTL — long-term task history requires a persistent result backend
- Debugging failed tasks requires inspecting worker logs or the Redis result backend
