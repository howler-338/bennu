# 0002 — Use Ollama for Self-Hosted LLM Inference

**Status:** Accepted

## Context

Bennu requires two AI capabilities: text embedding (for RAG) and chat generation. The options considered were:

- **Ollama** — Local model runner, serves models via HTTP API
- **OpenAI API** — Cloud-hosted embeddings (`text-embedding-3-small`) and chat (`gpt-4o`)
- **Hugging Face Inference API** — Cloud-hosted models
- **llama.cpp** — Direct local inference without an HTTP wrapper

For a portfolio project emphasizing cost optimization and privacy-first architecture, sending all document content to a third-party cloud API is a significant drawback — both in recurring cost and in the narrative the project communicates.

## Decision

Use Ollama running as a Docker container to serve both models locally:

- **Embedding:** `nomic-embed-text` — 768-dim vectors, fast on CPU, well-suited for RAG
- **Chat:** `llama3.2:3b` — 3B parameters, ~2 GB, responsive on modest hardware

The `services/embedder.py` and `services/llm.py` modules are the abstraction boundary. All Ollama-specific HTTP calls are isolated there, making future provider swaps surgical.

## Consequences

**Positive:**
- Zero per-token cloud AI cost — the entire inference stack runs on the VPS
- No document content leaves the server — strong privacy narrative for enterprise positioning
- Demonstrates self-hosted AI infrastructure expertise as a portfolio signal
- Provider abstraction enables future hybrid routing (local-first, cloud fallback)

**Negative:**
- Requires a VPS with sufficient RAM (8 GB minimum) — raises hosting cost vs a basic droplet
- Model quality is lower than GPT-4o class models
- Cold-start latency if Ollama unloads models from memory under low traffic
- No GPU acceleration in this deployment — inference is CPU-bound
