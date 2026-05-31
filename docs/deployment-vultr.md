# Deploying Bennu on Vultr

Self-hosted AI inference stack (~$60–80/mo) — no cloud AI API spend.

---

## Provisioned Instance

You have already provisioned an **Optimized Cloud Compute — Dedicated** instance. Confirm the specs match:

| Spec | Value |
|---|---|
| Type | Optimized Cloud Compute (Dedicated) |
| vCPU | 4 dedicated |
| RAM | 8 GB |
| OS | Ubuntu 24.04 |
| IPv4 | 1 public IP |

**Why dedicated vCPU?** Ollama inference is CPU-bound. Shared/burstable vCPUs throttle under concurrent embedding and chat requests. Dedicated vCPUs keep inference responsive during demos.

**Why 8 GB RAM?** Both AI models must be loaded simultaneously during a RAG request:

| Service | RAM |
|---|---|
| `llama3.2:3b` | ~2.5 GB |
| `nomic-embed-text` | ~0.6 GB |
| PostgreSQL + pgvector | ~0.5 GB |
| Gunicorn + Celery | ~0.7 GB |
| Redis + OS overhead | ~0.7 GB |
| **Total** | **~5.0 GB** |
| **Headroom** | **~3.0 GB** |

---

## Architecture

```
Internet
   │
   ▼ :80 / :443
[ Nginx container ]  ──── serves /assets/* directly from frontend/dist
   │
   │ proxy /api/* and /docs  (Docker network: backend:8000)
   ▼
[ Flask + Gunicorn container ]
   │
   ├── PostgreSQL + pgvector  (postgres_data volume)
   ├── Redis                  (Celery broker + rate limiter)
   ├── Celery worker          (document processing)
   ├── Celery beat            (retry stuck docs every 5 min)
   └── Ollama                 (ollama_data volume)
           ├── nomic-embed-text
           └── llama3.2:3b
```

All services run in Docker containers on the same network. Nginx resolves `backend:8000` via Docker DNS.

---

## Step 1 — Configure Vultr Firewall

In the Vultr control panel, go to **Network → Firewall → Add Firewall Group**, then attach it to your instance.

Allow inbound rules:

| Protocol | Port | Source |
|---|---|---|
| TCP | 22 (SSH) | Your IP only |
| TCP | 80 (HTTP) | Anywhere |
| TCP | 443 (HTTPS) | Anywhere |

Do **not** expose these — they are internal to Docker:

```
5432  PostgreSQL
6379  Redis
11434 Ollama
8000  Gunicorn
```

Add UFW on the server as a second layer of defense:

```bash
apt update && apt install -y ufw
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## Step 2 — Assign a Reserved IP (Optional but Recommended)

A Reserved IP survives instance rebuilds and lets you re-point a domain without a DNS TTL wait.

In the Vultr control panel: **Network → Reserved IPs → Add Reserved IP → Assign to your instance**.

Update your domain's A record to point at the reserved IP (or your instance IP if skipping this step).

---

## Step 3 — Point Your Domain

At your domain registrar, create an A record:

```
Type:  A
Host:  @
Value: YOUR_VULTR_IP
```

Optionally add `www`:

```
Type:  A
Host:  www
Value: YOUR_VULTR_IP
```

DNS must be live before Step 8 (SSL certificate).

---

## Step 4 — SSH Into the Server

```bash
ssh root@YOUR_VULTR_IP
```

---

## Step 5 — Install Dependencies

```bash
apt update && apt upgrade -y

# Docker
apt install -y docker.io docker-compose-plugin
systemctl enable docker
systemctl start docker

# Certbot (runs on host to obtain SSL certs, mounted into Nginx container)
apt install -y certbot

# Node.js LTS (to build the frontend)
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs

# Directories
mkdir -p /backups /var/www/certbot
```

---

## Step 6 — Clone and Configure

```bash
cd /root
git clone https://github.com/howler-338/bennu.git
cd bennu
cp .env.example .env
nano .env
```

Set these values:

```env
FLASK_ENV=production
SECRET_KEY=<run: python3 -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET_KEY=<run: python3 -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://bennu:bennu@postgres:5432/bennu
REDIS_URL=redis://redis:6379/0
OLLAMA_HOST=http://ollama:11434
EMBED_MODEL=nomic-embed-text
CHAT_MODEL=llama3.2:3b
FRONTEND_DIST=/app/dist
```

---

## Step 7 — Build the Frontend

```bash
cd /root/bennu/frontend
npm install
npm run build
cd ..
```

The build output lands in `frontend/dist/`, which is mounted into the Nginx container at runtime.

---

## Step 8 — Get SSL Certificate

Certbot uses standalone mode to obtain the initial certificate before Nginx starts:

```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Certs are stored in `/etc/letsencrypt/live/yourdomain.com/` and mounted read-only into the Nginx container.

---

## Step 9 — Configure Nginx

Replace the `DOMAIN` placeholder with your actual domain:

```bash
sed -i 's/DOMAIN/yourdomain.com/g' /root/bennu/infrastructure/nginx/nginx.conf
```

---

## Step 10 — Start All Services

```bash
cd /root/bennu
docker compose --profile production up -d
docker compose ps
```

Expected services: `backend`, `celery_worker`, `celery_beat`, `postgres`, `redis`, `ollama`, `nginx`

> **Note:** `docker compose up -d` without `--profile production` starts all services except Nginx — correct for local development where SSL certs don't exist.

---

## Step 11 — Run Migrations

```bash
docker compose exec backend flask db upgrade
```

---

## Step 12 — Pull AI Models

```bash
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2:3b
```

Model sizes: `nomic-embed-text` ~274 MB, `llama3.2:3b` ~2 GB.

---

## Step 13 — Create Admin Account

Register at `https://yourdomain.com/register`, then promote your account:

```bash
docker compose exec backend flask make-admin your@email.com
```

---

## Step 14 — SSL Auto-Renewal

Certbot uses the Nginx container to serve the ACME challenge for renewals:

```bash
crontab -e
```

Add:

```
0 3 * * * certbot renew --webroot -w /var/www/certbot --quiet && docker compose -f /root/bennu/docker-compose.yml restart nginx
```

---

## Step 15 — Automated Backups

**Vultr Automatic Backups** — Enable in the control panel: **Instance → Backups → Enable** (20% of instance cost, daily/weekly snapshots retained for 1 week).

**Daily Postgres dump** for point-in-time recovery:

```bash
crontab -e
```

Add:

```
0 2 * * * cd /root/bennu && docker compose exec -T postgres pg_dump -U bennu bennu | gzip > /backups/bennu_$(date +\%F).sql.gz
```

---

## Maintenance Commands

```bash
# View logs
docker compose logs backend -f
docker compose logs celery_worker -f
docker compose logs nginx -f

# Restart a service
docker compose restart backend
docker compose restart nginx

# Check all container status
docker compose --profile production ps
```

---

## Deploying Updates

```bash
cd /root/bennu
git pull

# Rebuild frontend
cd frontend && npm install && npm run build && cd ..

# Rebuild and restart backend
docker compose up -d --build backend

# Restart nginx to pick up new frontend dist
docker compose restart nginx

# Run any new migrations
docker compose exec backend flask db upgrade
```

---

## Comparison: Vultr vs Other Providers

| | Vultr | RackNerd | DigitalOcean |
|---|---|---|---|
| Firewall | Vultr Cloud Firewall (managed) + UFW | UFW only | DO Cloud Firewall (managed) |
| Reserved IP | Yes (control panel) | No | Yes (doctl) |
| Backups | Automatic backups (control panel) + cron | Cron only | DO Backups + cron |
| Managed DB | Vultr Managed MySQL/Postgres | No | DO Managed PostgreSQL |
| Cost | ~$60–80/mo | ~$20–35/mo | ~$84–101/mo |

---

## Estimated Cost

| Item | Cost |
|---|---|
| Optimized Cloud Compute Dedicated (8 GB) | ~$60–80/mo |
| Automatic Backups (20%) | ~$12–16/mo |
| Reserved IP | ~$3/mo |
| SSL Certificate (Let's Encrypt) | Free |
| **Total** | **~$75–99/mo** |
