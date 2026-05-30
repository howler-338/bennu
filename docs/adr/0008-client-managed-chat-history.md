# 0008 — Client-Managed Chat History

**Status:** Accepted

## Context

The RAG chat feature supports multi-turn conversations. Each turn requires prior messages as context for the LLM. Options for managing this history were:

- **Client-managed** — The frontend maintains the conversation array in memory and sends the full history with each request
- **Server-side sessions** — The backend stores conversation history in the database, keyed by session or conversation ID
- **Hybrid** — Server stores history but client sends a session ID

Server-side persistence requires a `conversations` table, a conversation ID per session, and additional API endpoints for history retrieval.

## Decision

The frontend maintains conversation history in React component state (`useState`). Each `POST /api/chat` request includes the full `history` array alongside the new `message`. The backend is stateless with respect to conversation — it receives context, runs RAG, and returns a reply.

## Consequences

**Positive:**
- Backend stays stateless — no conversation schema, no additional endpoints, no DB reads per turn
- Simpler implementation: the entire chat feature fits in a single endpoint
- No conversation data persisted — privacy benefit for sensitive document content

**Negative:**
- History is lost on page refresh or browser close
- Token usage grows with conversation length — no server-side truncation or summarization
- No cross-device or cross-session continuity
- Scaling to long conversations requires client-side token budget management (future work)

## Future

Server-side conversation persistence is planned as a future enhancement. The migration path is straightforward: add a `conversations` table, move the `history` array server-side, and expose a conversation ID in the API response.
