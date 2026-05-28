# Architecture

See [product-requirements.md](../product-requirements.md) for the full PRD.

## High-level flow

```text
[ React Frontend ]
        |
        v
[ Flask API Gateway ]
        |
        +--> Auth
        +--> Documents
        +--> Chat / RAG
        +--> Celery Workers
                  |
                  +--> Embedding Jobs
                  +--> Chunking / Indexing
```

## LLM abstraction

Routes must not call Ollama directly. Use `app.services.llm.get_llm_provider()` so cloud and hybrid providers can be added later.
