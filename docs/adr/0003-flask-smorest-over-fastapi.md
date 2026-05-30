# 0003 — Use Flask + Flask-Smorest over FastAPI

**Status:** Accepted

## Context

The backend requires a Python API framework with automatic OpenAPI documentation, request validation, and a clear blueprint/routing structure. The main candidates were:

- **Flask + Flask-Smorest** — Micro-framework with a Smorest layer for OpenAPI and marshmallow-based validation
- **FastAPI** — Modern async framework with Pydantic validation and built-in OpenAPI

FastAPI has become the default choice for new Python APIs. The decision to use Flask was deliberate.

## Decision

Use Flask 3.x with Flask-Smorest for OpenAPI/Swagger generation and marshmallow for serialization and validation.

## Consequences

**Positive:**
- Flask's blueprint system maps cleanly to domain modules (`auth`, `documents`, `search`, `chat`, `admin`)
- Flask-Smorest generates Swagger UI automatically from marshmallow schemas with minimal boilerplate
- Celery integrates naturally with Flask's application factory pattern via `make_celery`
- Flask is widely deployed in enterprise Python environments — familiar to more engineers

**Negative:**
- Flask is synchronous by default; long-running Ollama inference calls block a Gunicorn worker for the duration
- This is mitigated by Gunicorn's multi-worker model (4 workers) and Celery offloading document processing
- FastAPI's async support and Pydantic v2 would be more ergonomic for a greenfield project today
- Streaming responses (future feature) will require additional work compared to FastAPI's native streaming
