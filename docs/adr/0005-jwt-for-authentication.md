# 0005 — Use JWT for Authentication

**Status:** Accepted

## Context

Bennu requires user authentication with protected routes on both the API and frontend. The main patterns considered were:

- **JWT (JSON Web Tokens)** — Stateless tokens signed with a secret key, no server-side session store
- **Server-side sessions** — Session ID stored in a cookie, session data stored server-side (Redis or DB)
- **OAuth / SSO** — Delegated auth via a third-party identity provider

## Decision

Use Flask-JWT-Extended with an access token + refresh token pattern. Access tokens are short-lived and sent as `Authorization: Bearer <token>` headers. The frontend stores tokens in `localStorage` via Zustand with persistence.

The API client intercepts 401 responses, clears auth state, and redirects to `/login` — handling expired tokens transparently.

## Consequences

**Positive:**
- Stateless — no session store required, Gunicorn workers share no auth state
- Scales horizontally without sticky sessions or shared session storage
- Standard pattern for API-first architectures; familiar to enterprise engineers
- Access + refresh token split limits exposure window for compromised access tokens

**Negative:**
- Tokens stored in `localStorage` are accessible to JavaScript — XSS is a risk; `httpOnly` cookies would be more secure
- No server-side token revocation without a token denylist (future: add Redis-backed denylist on logout)
- JWT expiry is checked client-side on 401 — a compromised token is valid until expiry unless a denylist is implemented
