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
- React
- Vite
- TypeScript
- Tailwind CSS

### Future Enhancements
- Zustand or Redux
- React Query
- Component library
- Dark mode support

---

## Backend

### Core Technologies
- Flask
- Flask-Smorest (OpenAPI/Swagger docs, request validation)
- marshmallow (serialization and schema validation)
- Flask-SQLAlchemy + Flask-Migrate
- Flask-JWT-Extended
- Celery
- Redis

### Responsibilities
- API gateway
- Authentication
- Chat orchestration
- Document management
- RAG coordination
- Model abstraction layer
- Background job management

---

## Database

### Primary Database
- PostgreSQL

### Vector Storage
- pgvector

### Responsibilities
- User data
- Metadata
- Document indexing
- Embedding storage
- Conversation history
- Audit logs

---

## AI Infrastructure

### Local Inference
- Ollama

### Suggested Models
#### Chat Models
- Llama 3 8B
- Mistral 7B
- Phi-3

#### Embedding Models
- nomic-embed-text
- bge-small
- mxbai-embed-large

---

## Infrastructure

### Local Development
- Docker
- Docker Compose

### Production Infrastructure (Future)
- Kubernetes
- Terraform
- GitHub Actions

---

# High-Level Architecture

```text
[ React Frontend ]
        |
        v
[ Flask API Gateway ]
        |
        +--> Auth Service
        |
        +--> Document Service
        |
        +--> Chat Service
        |
        +--> RAG Pipeline
        |
        +--> Celery Workers
                  |
                  +--> Embedding Jobs
                  +--> OCR Jobs
                  +--> Chunking Jobs
                  +--> Indexing Jobs
```

---

# Product Features

# MVP Scope

The MVP should prioritize architecture quality and backend workflows over UI complexity.

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
- Endpoints: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/refresh`

### Future Enhancements
- OAuth
- SSO
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
- All routes JWT-protected

### Constraints
- File size limit: 50MB
- Allowed MIME types: PDF, plain text, DOCX
- Virus scanning (future)

---

## Feature 3 — Document Processing Pipeline 🔄 In Progress

### Requirements
Uploaded documents should:

1. Be parsed
2. Be chunked
3. Generate embeddings
4. Store vectors in pgvector
5. Become searchable

### Processing Requirements
- Async processing using Celery
- Retry mechanisms
- Job status tracking
- Failure handling
- Queue monitoring

---

## Feature 4 — Semantic Search

### Requirements
Users should be able to:

- Search documents semantically
- Retrieve relevant chunks
- Filter search results
- View similarity scores

### Technical Requirements
- Vector similarity search
- Embedding generation
- Search ranking

---

## Feature 5 — RAG Chat

### Requirements
Users should be able to:

- Ask questions about uploaded documents
- Receive contextual answers
- Receive cited responses
- Maintain conversation history

### System Requirements
- Context retrieval
- Prompt construction
- Model routing
- Token optimization
- Streaming responses (future)

---

## Feature 6 — Admin Dashboard

### Requirements
Administrators should be able to:

- View ingestion jobs
- Monitor processing pipelines
- View model usage
- View system metrics
- Monitor failures

---

# AI Architecture

# LLM Provider Abstraction Layer

The platform should NOT tightly couple routes directly to Ollama.

Instead, implement a provider abstraction layer.

## Example Interface

```python
class LLMProvider:
    def generate_response(self, prompt):
        pass
```

---

## Planned Providers

### OllamaProvider
Handles:
- Local inference
- Embeddings
- Chat generation

### OpenAIProvider (Future)
Handles:
- Cloud inference
- Failover
- Hybrid routing

### HybridProvider (Future)
Handles:
- Local-first routing
- Cost optimization
- Fallback inference

---

# Backend Architecture

# Suggested Backend Structure

```text
backend/
├── app/
│   ├── api/
│   ├── auth/
│   ├── chat/
│   ├── documents/
│   ├── embeddings/
│   ├── rag/
│   ├── services/
│   ├── workers/
│   └── config/
│
├── migrations/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

# Frontend Architecture

# Suggested Frontend Structure

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── services/
│   ├── layouts/
│   ├── types/
│   └── utils/
│
├── public/
└── vite.config.ts
```

---

# Infrastructure Structure

```text
infrastructure/
├── docker/
├── terraform/
└── kubernetes/
```

---

# Repository Structure

```text
bennu/
├── frontend/
├── backend/
├── infrastructure/
├── docs/
├── screenshots/
├── .github/
├── docker-compose.yml
└── README.md
```

---

# Non-Functional Requirements

# Scalability

The architecture should support:

- Horizontal API scaling
- Background worker scaling
- Separate inference services
- Distributed processing
- Future multi-tenant architecture

---

# Reliability

The platform should implement:

- Retry mechanisms
- Queue durability
- Health checks
- Graceful failure handling
- Logging
- Monitoring

---

# Security

The platform should consider:

- JWT authentication
- Role-based access control
- Secret management
- File validation
- API rate limiting
- Secure environment variables

---

# Observability

The platform should support:

- Structured logging
- Metrics collection
- Error monitoring
- Queue visibility
- Request tracing

### Future Enhancements
- Prometheus
- Grafana
- OpenTelemetry

---

# Deployment Strategy

# Local Development

Use:
- Docker Compose

Services:
- frontend
- backend
- postgres
- redis
- ollama
- celery worker

---

# Production Deployment (Future)

### Kubernetes Deployment
Components:
- Frontend deployment
- API deployment
- Worker deployment
- PostgreSQL
- Redis
- Ollama inference nodes

### Infrastructure as Code
- Terraform

---

# Architecture Priorities

# Priority Order

## Priority #1
Architecture quality

## Priority #2
Documentation quality

## Priority #3
Deployment maturity

## Priority #4
Code quality

## Priority #5
UI polish

---

# README Requirements

The repository README should include:

- Executive summary
- Architecture diagrams
- Technology stack
- Setup instructions
- Deployment instructions
- Scalability considerations
- Security considerations
- Future roadmap

---

# Consulting Positioning

The project should position the developer as experienced in:

- AI platform architecture
- Self-hosted AI infrastructure
- RAG systems
- Cloud-native deployment
- Cost optimization
- Enterprise AI integration
- Distributed systems
- Platform engineering

---

# Future Enhancements

## AI Enhancements
- Multi-model routing
- Hybrid local/cloud inference
- Agent workflows
- Tool calling
- Long-term memory

---

## Enterprise Enhancements
- Multi-tenancy
- RBAC
- Audit logs
- SSO
- Enterprise permissions

---

## Infrastructure Enhancements
- Kubernetes autoscaling
- GPU scheduling
- Service mesh
- Multi-region deployment
- Disaster recovery

---

# Initial Development Roadmap

# Week 1 ✅ Complete

## Goals
- Create repository ✅
- Create project structure ✅
- Configure Docker Compose ✅
- Configure PostgreSQL ✅
- Configure Redis ✅
- Configure Flask API ✅
- Configure React frontend (deferred to Week 2)

---

# Week 2 🔄 In Progress

## Goals
- Implement authentication ✅
- Implement document upload ✅
- Integrate Flask-Smorest + OpenAPI docs ✅
- Implement document processing pipeline (Celery + embeddings)
- Implement document chunking
- Store vectors in pgvector
- Integrate Ollama

---

# Week 3

## Goals
- Implement semantic search
- Implement RAG pipeline
- Implement chat interface
- Add conversation history

---

# Week 4

## Goals
- Add monitoring
- Add logging
- Add retry mechanisms
- Improve documentation
- Create architecture diagrams
- Polish README
- Scaffold React frontend

---

# Confirmed Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector storage | pgvector (PostgreSQL extension) | Reduces infrastructure complexity — no separate vector DB needed |
| API framework | Flask-Smorest | Auto-generates OpenAPI docs, marshmallow validation, clean blueprint structure |
| Auth strategy | JWT (access + refresh tokens) | Stateless, scalable, enterprise-standard |
| Local dev | Docker Compose | Zero-setup, consistent across machines, close to production |
| Embedding model | TBD (nomic-embed-text or bge-small via Ollama) | Decision pending Feature 3 implementation |
| LLM for chat | TBD (Llama 3 8B or Mistral 7B via Ollama) | Decision pending Feature 5 implementation |

---

# Long-Term Vision

Bennu should eventually evolve into:

- A consulting showcase platform
- A reusable enterprise AI starter platform
- A SaaS AI knowledge product
- A hybrid AI infrastructure demo
- A lead-generation asset for consulting services

---

# Recommended GitHub Description

> Enterprise AI knowledge platform using RAG, vector search, and self-hosted LLM inference with Ollama.

---

# Repository Visibility Strategy

## Repository Type
Public

## Licensing Strategy
No license initially to preserve future SaaS and commercialization flexibility.

---

# Key Portfolio Messaging

This project should communicate:

- Senior engineering capability
- Enterprise architecture thinking
- AI systems expertise
- Production deployment maturity
- Cost optimization awareness
- Cloud-native engineering practices
- Consulting-level communication and documentation

