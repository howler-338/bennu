# 0006 — Use Docker Compose for All Environments

**Status:** Accepted

## Context

Bennu depends on six services: Flask/Gunicorn, Celery worker, Celery beat, PostgreSQL + pgvector, Redis, and Ollama. Coordinating these across local development and production requires a consistent approach.

Options considered:

- **Docker Compose** — Single YAML file defines and starts all services
- **Kubernetes** — Container orchestration for production, local dev via minikube or kind
- **Manual installation** — Each service installed directly on the host
- **Separate local/prod configs** — Different tooling per environment

## Decision

Use Docker Compose for both local development and production. A single `docker-compose.yml` defines all services. A `production` profile activates the Nginx container (which requires SSL certs that don't exist in local dev).

Local dev: `docker compose up -d`
Production: `docker compose --profile production up -d`

## Consequences

**Positive:**
- Zero-setup local development — one command starts the full stack including pgvector and Ollama
- Production environment closely mirrors local, reducing "works on my machine" issues
- No Kubernetes complexity for a single-VPS deployment
- Docker volumes provide persistent storage for Postgres, Redis, Ollama models, and file uploads

**Negative:**
- Docker Compose does not provide automatic failover, rolling deploys, or health-based rescheduling — Kubernetes would be required for those
- The `celery-common` YAML anchor duplicates environment config between `backend` and Celery services — a production override file would be cleaner but adds complexity
- Source code is volume-mounted in the current config (`./backend:/app`), which is a dev convenience but should be removed in a hardened production image
