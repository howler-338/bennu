# Product Requirements Document — Bennu

> **Status:** Draft  
> **Last updated:** 2026-05-29  
> **Owner:** TBD

---

## 1. Overview

Bennu is an enterprise AI knowledge platform that gives organizations a private, self-hosted way to query and reason over their internal knowledge base. It combines retrieval-augmented generation (RAG), vector search, and on-premise LLM inference via Ollama — keeping sensitive data off third-party APIs.

---

## 2. Problem Statement

Enterprise teams struggle to extract value from scattered internal knowledge (docs, wikis, code, tickets). Existing solutions either require sending data to third-party LLM APIs (privacy/compliance risk) or demand significant ML infrastructure expertise to self-host.

---

## 3. Goals

- Enable employees to query internal knowledge using natural language
- Keep all data and inference on-premise (no external LLM API calls required)
- Deliver accurate, cited answers grounded in source documents
- Be deployable by a small infrastructure team without ML expertise

---

## 4. Non-Goals

- Real-time data ingestion (initial version is batch/scheduled)
- Consumer-facing product (enterprise B2B only)
- Fine-tuning or training models from scratch
- Replacing a dedicated search engine (Elasticsearch, etc.) for structured queries

---

## 5. Users

| Persona | Description | Primary Need |
|---------|-------------|--------------|
| Knowledge Worker | Employee querying internal docs, wikis, runbooks | Fast, accurate answers with source citations |
| IT / Infra Admin | Deploys and maintains the platform | Simple setup, monitoring, access control |
| Content Owner | Uploads and manages knowledge sources | Control over what gets indexed and who can query it |

---

## 6. Requirements

### 6.1 Functional Requirements

#### Ingestion
- [ ] Ingest documents from common formats: PDF, Markdown, DOCX, plain text
- [ ] Ingest from common sources: local filesystem, S3-compatible storage, Confluence, Notion
- [ ] Chunk documents with configurable overlap and chunk size
- [ ] Generate and store embeddings in a vector database

#### Retrieval
- [ ] Semantic search over ingested content via vector similarity
- [ ] Hybrid search (vector + keyword) with configurable weights
- [ ] Metadata filtering (date range, source, tags, department)
- [ ] Return top-K results with relevance scores

#### Generation
- [ ] Route retrieved context + user query to a local Ollama model
- [ ] Support swappable models (Llama, Mistral, Gemma, etc.)
- [ ] Stream responses to the client
- [ ] Include source citations with every answer

#### Access & Auth
- [ ] Role-based access control (admin, user, read-only)
- [ ] SSO integration (SAML / OIDC)
- [ ] Per-collection access permissions

#### API
- [ ] REST API for query and ingestion
- [ ] Webhook support for ingestion pipeline triggers

#### UI
- [ ] Chat interface for natural language queries
- [ ] Source viewer (view the source chunk that grounded each answer)
- [ ] Admin dashboard: ingestion status, model health, usage stats

### 6.2 Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Latency | P95 query response < 5s for typical document corpus |
| Scalability | Support corpora up to 10M document chunks |
| Availability | 99.5% uptime target for query path |
| Privacy | No data leaves the deployment environment |
| Observability | Structured logs, metrics endpoint (Prometheus-compatible) |
| Deployment | Docker Compose for single-node; Helm chart for Kubernetes |

---

## 7. Architecture Snapshot

```
User
 │
 ▼
API Layer (REST / WebSocket)
 │
 ├─► Retrieval Engine
 │      ├─ Vector DB (e.g., Qdrant / Weaviate / pgvector)
 │      └─ Keyword Index (optional)
 │
 └─► Generation Engine
        └─ Ollama (local LLM inference)

Ingestion Pipeline (async)
 └─ Document Loader → Chunker → Embedder → Vector DB
```

---

## 8. Milestones

| Milestone | Description | Target |
|-----------|-------------|--------|
| M1 — Core RAG loop | Ingest PDFs + Markdown, query via CLI, Ollama-backed answers | TBD |
| M2 — Web UI | Chat interface, source viewer, basic auth | TBD |
| M3 — Admin & Access Control | RBAC, SSO, per-collection permissions | TBD |
| M4 — Connectors | Confluence, Notion, S3 ingestion | TBD |
| M5 — Production Hardening | Helm chart, observability, performance tuning | TBD |

---

## 9. Open Questions

- [ ] Which vector database to use as the primary target? (Qdrant, Weaviate, pgvector, Chroma)
- [ ] Embedding model strategy — local (via Ollama) or a dedicated embedder (sentence-transformers)?
- [ ] Multi-tenancy model: single deployment per org or multi-tenant SaaS-style?
- [ ] What is the initial supported deployment target: Docker Compose only, or Kubernetes from day one?
- [ ] Reranking step in retrieval pipeline (e.g., cross-encoder reranker)?

---

## 10. Change Log

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-29 | — | Initial draft |
