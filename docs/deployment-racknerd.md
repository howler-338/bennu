# Deploying Bennu on RackNerd

Budget self-hosted AI inference stack (~$20–35/mo) — no cloud AI API spend.

---

## Recommended VPS

Choose a **KVM / Ryzen NVMe Linux VPS** with at least:

| Spec | Minimum |
|---|---|
| RAM | **8 GB** |
| vCPU | **4 vCPU** |
| Disk | **100 GB SSD/NVMe** |
| OS | **Ubuntu 24.04** |
| IPv4 | 1 public IP |

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

> **Do not use a 4 GB VPS.** OOM kills during a demo are a credibility risk.

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

All services run in Docker containers on the same network. Nginx resolves `backend:8000` via Docker DNS — no host port exposure needed for internal services.

---

## Step 1 — Order VPS and Get Credentials

After purchase, RackNerd emails you:

```
VPS IP address
Root password
SolusVM control panel login
```

Select **Ubuntu 24.04** as the OS. If unavailable, use 22.04.

---

## Step 2 — Point Your Domain

At your domain registrar, create an A record:

```
Type:  A
Host:  @
Value: YOUR_RACKNERD_IP
```

Optionally add `www`:

```
Type:  A
Host:  www
Value: YOUR_RACKNERD_IP
```

DNS propagation typically takes a few minutes but can take up to 24 hours. SSL setup in Step 8 requires DNS to be live.

---

## Step 3 — SSH Into the Server

```bash
ssh root@YOUR_RACKNERD_IP
```

---

## Step 4 — Firewall with UFW

RackNerd has no managed cloud firewall — use UFW on the server. Only ports 22, 80, and 443 should be publicly reachable. Everything else is internal to Docker.

```bash
apt update && apt install -y ufw

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

---

## Step 5 — Install Dependencies

```bash
apt update && apt upgrade -y

# Docker
apt install -y docker.io docker-compose-plugin
systemctl enable docker
systemctl start docker

# Certbot (runs on host to obtain SSL certs)
apt install -y certbot

# Node.js LTS (to build the frontend)
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs

# Backup directory and certbot webroot
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

Certbot runs on the host using standalone mode to obtain the initial certificate (before Nginx starts):

```bash
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Certs are stored in `/etc/letsencrypt/live/yourdomain.com/` and mounted read-only into the Nginx container.

---

## Step 9 — Configure Nginx

Replace the `DOMAIN` placeholder in the nginx config with your actual domain:

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

> **Note:** `docker compose up -d` without `--profile production` starts all services except Nginx — useful for local development where SSL certs don't exist.

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

Model sizes: `nomic-embed-text` ~274 MB, `llama3.2:3b` ~2 GB. Download time depends on VPS bandwidth.

---

## Step 13 — Create Admin Account

Register at `https://yourdomain.com/register`, then promote your account:

```bash
docker compose exec backend flask make-admin your@email.com
```

---

## Step 14 — SSL Auto-Renewal

Certbot uses the Nginx container to serve the ACME challenge for renewals. Add a cron job:

```bash
crontab -e
```

Add:

```
0 3 * * * certbot renew --webroot -w /var/www/certbot --quiet && docker compose -f /root/bennu/docker-compose.yml restart nginx
```

---

## Step 15 — Automated Database Backup

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

## Key Differences from DigitalOcean

| | RackNerd | DigitalOcean |
|---|---|---|
| Firewall | UFW on server | DO Cloud Firewall (managed) |
| IP | Assigned VPS IP | Reserved IP (survives rebuilds) |
| Backups | Cron + pg_dump | DO Backups panel + cron |
| Cost | ~$20–35/mo | ~$84–101/mo |
| Managed DB option | No | DO Managed PostgreSQL |

---

## Estimated Cost

| Item | Cost |
|---|---|
| RackNerd KVM VPS (8 GB RAM) | ~$20–35/mo |
| SSL Certificate (Let's Encrypt) | Free |
| **Total** | **~$20–35/mo** |
