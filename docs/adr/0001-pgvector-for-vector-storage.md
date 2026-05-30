# 0001 — Use pgvector for Vector Storage

**Status:** Accepted

## Context

Bennu requires vector storage to support semantic search and RAG. The main options considered were:

- **pgvector** — PostgreSQL extension adding a vector column type and cosine similarity search
- **Pinecone** — Managed cloud vector database
- **Weaviate** — Self-hosted or managed vector database
- **Chroma** — Lightweight embedded vector store

Adding a dedicated vector database means running and operating an additional service, adding operational complexity, network hops between services, and (for managed options) recurring cloud spend.

## Decision

Use pgvector as a PostgreSQL extension alongside the primary database.

Document chunks and their embeddings are stored in the `document_chunks` table with a `Vector(768)` column. Cosine similarity search is performed with a single SQL query via SQLAlchemy.

## Consequences

**Positive:**
- No additional service to run, monitor, or back up — vectors live in the same Postgres instance already required for user and document data
- Transactional consistency between document metadata and its embeddings
- Single backup covers all data
- Cosine similarity search at 768 dimensions is fast enough for single-tenant workloads

**Negative:**
- Does not scale as well as purpose-built vector databases for very large corpora (millions of chunks)
- No built-in hybrid search (BM25 + vector) — would require additional Postgres extensions
- ANN (approximate nearest neighbor) index support is less mature than dedicated vector DBs
