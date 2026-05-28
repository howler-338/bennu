# Setup

## Prerequisites

- Docker & Docker Compose
- Node.js 22+ (local frontend dev)
- npm **11.10.0+** (for `min-release-age` supply-chain protection in `frontend/.npmrc`)
- Python 3.12+ (local backend dev)

### npm supply-chain protection

`frontend/.npmrc` sets `min-release-age=7` (7 **days**, not `7d`). npm rejects versions published more recently than that during `npm install` / `npm ci`.

Upgrade npm if needed:

```bash
npm install -g npm@latest
npm --version   # should be >= 11.10.0
```

To install a specific new package immediately (override once):

```bash
npm install some-package --min-release-age=0
```

## Quick start (Docker)

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

| Service        | URL                    |
|----------------|------------------------|
| Frontend       | http://localhost:5173  |
| API            | http://localhost:5000  |
| Health check   | http://localhost:5000/health |
| Ollama         | http://localhost:11434 |

Pull models into Ollama:

```bash
docker compose exec ollama ollama pull llama3
docker compose exec ollama ollama pull nomic-embed-text
```

## Local development

### Backend

On macOS, use `python3` (there is often no `python` command):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; defaults work for a minimal run
export FLASK_APP=wsgi:app
flask run
```

If `flask` is not found after activate, use:

```bash
python -m flask run
```

The health check works without Postgres: http://127.0.0.1:5000/health

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Celery worker

```bash
cd backend
celery -A app.workers.celery_app:celery worker --loglevel=info
```
