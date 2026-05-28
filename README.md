# Bennu

Enterprise AI knowledge platform using RAG, vector search, and self-hosted LLM inference with Ollama.

## Overview

Bennu is a cloud-native knowledge platform that demonstrates:

- Retrieval-Augmented Generation (RAG)
- Vector search with pgvector
- Async document processing with Celery
- Self-hosted inference via Ollama
- Modular Flask API with LLM provider abstraction

## Repository structure

```text
bennu/
├── frontend/          # React + Vite + TypeScript + Tailwind
├── backend/           # Flask API, Celery workers, RAG services
├── infrastructure/    # Docker, Terraform, Kubernetes (planned)
├── docs/              # Architecture and setup guides
├── screenshots/       # Portfolio screenshots
├── docker-compose.yml
└── product-requirements.md
```

## Technology stack

| Layer        | Technologies                          |
|--------------|---------------------------------------|
| Frontend     | React, Vite, TypeScript, Tailwind CSS |
| Backend      | Flask, Celery, Redis                  |
| Database     | PostgreSQL, pgvector                  |
| AI           | Ollama (chat + embeddings)            |
| Infra        | Docker Compose (local)                |

## Quick start

See [docs/setup.md](docs/setup.md) for full instructions.

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- API health: http://localhost:5000/health

## Documentation

- [Product requirements](product-requirements.md)
- [Architecture](docs/architecture.md)
- [Setup guide](docs/setup.md)

## Roadmap

See the development roadmap in [product-requirements.md](product-requirements.md#initial-development-roadmap).
