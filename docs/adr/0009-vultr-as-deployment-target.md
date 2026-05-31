# 0009 — Use Vultr as Primary Deployment Target

**Status:** Accepted

## Context

Bennu requires a VPS with at least 8 GB RAM and 4 dedicated vCPUs to run the full stack (Ollama, PostgreSQL, Redis, Gunicorn, Celery) without OOM pressure. Three providers were evaluated:

- **DigitalOcean** — Polished DX, managed services (PostgreSQL, Spaces), `doctl` CLI, reserved IPs. CPU-Optimized 4 vCPU / 8 GB costs ~$84/mo.
- **RackNerd** — Budget-focused, no managed services, no cloud firewall, UFW only. KVM 8 GB costs ~$20–35/mo.
- **Vultr** — Mid-tier, Optimized Cloud Compute Dedicated 4 vCPU / 8 GB costs ~$60–80/mo. Managed cloud firewall, reserved IPs, automatic backups, and managed database available.

An 8 GB RAM instance was already provisioned on Vultr prior to this decision being formally recorded.

## Decision

Use Vultr Optimized Cloud Compute (Dedicated) as the active deployment target. A deployment guide has been added at `docs/deployment-vultr.md`.

The deployment model is identical to the RackNerd and DigitalOcean guides: Docker Compose with a `production` profile for Nginx, Certbot on the host for SSL, and all other services containerized.

## Consequences

**Positive:**
- Dedicated vCPUs prevent CPU throttling during Ollama inference — consistent demo performance
- Vultr Cloud Firewall provides managed inbound rules via the control panel, without relying solely on UFW
- Reserved IPs allow domain re-pointing without DNS TTL wait if the instance is rebuilt
- Automatic Backups (control panel) provide weekly snapshots; combined with the pg_dump cron for daily point-in-time recovery
- Meaningfully cheaper than DigitalOcean for equivalent dedicated compute

**Negative:**
- No equivalent to DO Managed PostgreSQL at the same price tier — Postgres runs in Docker on the same instance
- Vultr's managed database and object storage options exist but add cost, removing the budget advantage over DigitalOcean
- Less community documentation and ecosystem tooling than DigitalOcean (`vultr-cli` is less mature than `doctl`)
