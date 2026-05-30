# 0007 — Run Nginx in Docker for SSL Termination

**Status:** Accepted

## Context

The production deployment needs SSL termination and static file serving for the React frontend. The options considered were:

- **Nginx in Docker** — Nginx container on the same Docker network as the backend, proxying via Docker DNS (`backend:8000`)
- **Nginx on host** — Nginx installed directly on the VPS, proxying to `localhost:8000`
- **Caddy** — Alternative reverse proxy with automatic HTTPS via Let's Encrypt
- **Flask serving everything** — Gunicorn serves both the API and the frontend static files, no reverse proxy

## Decision

Run Nginx as a Docker container under a `production` Compose profile. It shares the Docker network with the backend, so `backend:8000` resolves via Docker DNS without exposing the backend port to the host.

Certbot runs on the host (not in Docker) and obtains certificates via standalone mode on first run. The `/etc/letsencrypt` directory is mounted read-only into the Nginx container. Renewals use the webroot method, with `/var/www/certbot` mounted into the Nginx container to serve the ACME challenge.

The `production` profile means `docker compose up -d` in local development does not start Nginx (no SSL certs present locally).

## Consequences

**Positive:**
- Nginx handles static asset serving with aggressive caching (`Cache-Control: public, immutable, 1y`) — no Gunicorn workers consumed for static files
- Backend port is not exposed to the host; all external traffic enters through Nginx on 80/443
- Consistent with the "everything in Docker" philosophy
- Profile-based activation keeps local dev unaffected

**Negative:**
- Certbot runs on the host, creating a split: cert lifecycle is managed outside Docker while Nginx is inside
- First-deploy sequence must be precise: get cert (standalone) → then start Nginx container
- Cert renewal requires the Nginx container to be restarted after renewal to pick up new certs
