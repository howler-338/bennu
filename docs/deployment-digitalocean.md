# Deploying Bennu on DigitalOcean

Self-hosted AI inference stack ($82/mo) — no cloud AI API spend.

---

## Recommended Droplet

| Spec | Value |
|---|---|
| Type | CPU-Optimized |
| vCPU | 4 dedicated |
| RAM | 8 GB |
| Storage | 100 GB NVMe SSD |
| Region | `SFO3` or `NYC3` |
| Est. cost | ~$84/mo |

**Why CPU-Optimized?** Ollama inference is CPU-bound without a GPU. Shared/burstable vCPUs throttle under concurrent embedding and chat requests, producing poor demo performance. Dedicated vCPUs keep inference responsive.

**Why 8 GB RAM?** With both models loaded simultaneously:

| Service | RAM |
|---|---|
| `llama3.2:3b` | ~2.5 GB |
| `nomic-embed-text` | ~0.6 GB |
| PostgreSQL + pgvector | ~0.5 GB |
| Gunicorn + Celery | ~0.7 GB |
| Redis + OS overhead | ~0.7 GB |
| **Total** | **~5.0 GB** |
| **Headroom** | **~3.0 GB** |

The 3 GB headroom lets Ollama keep both models hot — no swapping between embedding and chat generation in the same RAG request.

> **Do not use a 4 GB droplet.** It is the hard floor and leaves no headroom once all containers are running. OOM kills during a demo are a credibility risk.

---

## Architecture on the Droplet

```
Internet
   │
   ▼ :80 / :443
[ Nginx ]  ──── serves /assets/* directly from frontend/dist
   │
   │ proxy /api/* and /docs
   ▼ :8000
[ Flask + Gunicorn (4 workers) ]
   │
   ├── PostgreSQL + pgvector  (postgres_data volume)
   ├── Redis                  (Celery broker + rate limiter)
   ├── Celery worker          (document processing)
   ├── Celery beat            (retry stuck docs every 5 min)
   └── Ollama                 (ollama_data volume)
           ├── nomic-embed-text
           └── llama3.2:3b
```

---

## Prerequisites

On your local machine:
- `doctl` CLI installed and authenticated (`doctl auth init`)
- SSH key added to your DigitalOcean account

---

## Step 1 — Provision the Droplet

```bash
doctl compute droplet create bennu \
  --image ubuntu-24-04-x64 \
  --size c-4 \
  --region sfo3 \
  --ssh-keys <your-ssh-key-id>
```

Get your SSH key ID: `doctl compute ssh-key list`

---

## Step 2 — Assign a Reserved IP

Do this immediately — before pointing a domain at the droplet. A reserved IP is free and survives droplet rebuilds.

```bash
doctl compute reserved-ip create --region sfo3
doctl compute reserved-ip assign <reserved-ip> --droplet-id <droplet-id>
```

Point your domain's A record at the reserved IP.

---

## Step 3 — Configure the Firewall

```bash
doctl compute firewall create \
  --name bennu-fw \
  --inbound-rules "protocol:tcp,ports:22,address:YOUR_IP/32 protocol:tcp,ports:80,address:0.0.0.0/0,::/0 protocol:tcp,ports:443,address:0.0.0.0/0,::/0" \
  --outbound-rules "protocol:tcp,ports:all,address:0.0.0.0/0 protocol:udp,ports:all,address:0.0.0.0/0"
```

Ports **5432** (Postgres), **6379** (Redis), **11434** (Ollama), and **8000** (Gunicorn) must **never** be exposed publicly — they communicate only over the internal Docker network.

---

## Step 4 — Initial Server Setup

```bash
ssh root@<reserved-ip>

# Install Docker
apt update && apt install -y docker.io docker-compose-plugin

# Install Nginx and Certbot
apt install -y nginx certbot python3-certbot-nginx

# Create backup directory
mkdir -p /backups
```

---

## Step 5 — Clone and Configure

```bash
git clone https://github.com/howler-338/bennu.git
cd bennu
cp .env.example .env
```

Edit `.env` — set real values for all required variables:

```bash
nano .env
```

Key variables to set:
```
FLASK_ENV=production
SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://bennu:bennu@postgres:5432/bennu
REDIS_URL=redis://redis:6379/0
OLLAMA_HOST=http://ollama:11434
FRONTEND_DIST=/app/dist
```

---

## Step 6 — Configure Nginx

Copy the config and replace `DOMAIN` with your actual domain:

```bash
cp infrastructure/nginx/nginx.conf /etc/nginx/conf.d/bennu.conf
sed -i 's/DOMAIN/yourdomain.com/g' /etc/nginx/conf.d/bennu.conf
```

Test and reload:

```bash
nginx -t && systemctl reload nginx
```

---

## Step 7 — Get a Free SSL Certificate

```bash
certbot --nginx -d yourdomain.com
```

Certbot automatically edits the nginx config with the certificate paths and sets up auto-renewal via a systemd timer.

Verify auto-renewal: `certbot renew --dry-run`

---

## Step 8 — Build the Frontend

```bash
cd /root/bennu/frontend
npm install && npm run build
cd ..
```

---

## Step 9 — Start All Services

```bash
docker compose up -d
```

Verify all containers are running:
```bash
docker compose ps
```

Expected services: `backend`, `celery_worker`, `celery_beat`, `postgres`, `redis`, `ollama`

---

## Step 10 — Run Migrations

```bash
docker compose exec backend flask db upgrade
```

---

## Step 11 — Pull AI Models

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2:3b
```

Model sizes: `nomic-embed-text` ~274 MB, `llama3.2:3b` ~2 GB. Download time depends on droplet bandwidth.

---

## Step 12 — Create Admin Account

Register at `https://yourdomain.com/register`, then promote your account:

```bash
docker compose exec backend flask make-admin your@email.com
```

---

## Step 13 — Enable Automated Backups

Enable from the DigitalOcean control panel: **Droplet → Backups → Enable** ($14/mo, weekly snapshots).

Add a daily Postgres dump:

```bash
crontab -e
```

```
0 2 * * * cd /root/bennu && docker compose exec -T postgres pg_dump -U bennu bennu | gzip > /backups/bennu_$(date +\%F).sql.gz
```

---

## Maintenance Commands

```bash
# View logs
docker compose logs backend -f
docker compose logs celery_worker -f

# Restart a service
docker compose restart backend

# Deploy an update
git pull
cd frontend && npm run build && cd ..
docker compose up -d --build backend

# Run migrations after update
docker compose exec backend flask db upgrade

# Run tests
docker compose exec backend pytest -v
```

---

## Monthly Cost

| Item | Cost |
|---|---|
| CPU-Optimized Droplet (4 vCPU, 8 GB) | ~$84 |
| Automated Backups (20%) | ~$17 |
| Reserved IP | Free |
| SSL Certificate (Let's Encrypt) | Free |
| **Total** | **~$101/mo** |

---

## Scaling Path

Execute in this order as usage grows:

### Phase 1 — Managed PostgreSQL (~$15/mo added)
Move Postgres to **DO Managed PostgreSQL**. Gains point-in-time recovery, automated backups, and PgBouncer connection pooling. Remove the `postgres` service from `docker-compose.yml` and update `DATABASE_URL`.

### Phase 2 — Object Storage for Uploads (~$5/mo added)
Move `uploads_data` volume to **DO Spaces** (S3-compatible). Update `UPLOAD_FOLDER` to point at a Spaces bucket via `boto3`. Uploaded files then survive droplet rebuilds without volume migration.

### Phase 3 — Separate Celery Droplet
Spin up a second Standard droplet running only `celery_worker` and `celery_beat`, pointed at the same Redis and Postgres. Isolates CPU-heavy document processing from API latency and allows independent scaling.

### Phase 4 — CI/CD
GitHub Actions: run 41-test suite → build frontend → SSH deploy on push to `main`.

---

## Portfolio Messaging

This deployment demonstrates:

- **Cost optimization** — full AI inference stack for ~$100/mo with zero cloud AI API spend
- **Self-hosted inference** — privacy-first, no data leaving the droplet
- **Production-grade ops** — Nginx + SSL, Gunicorn, automated backups, firewall, rate limiting
- **Scalable foundations** — clear upgrade path to managed DB, object storage, and multi-node without re-architecting
