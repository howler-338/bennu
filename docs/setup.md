# Setup

## Prerequisites

- Docker & Docker Compose
- Node.js 22+ (local frontend dev)
- Python 3.12+ (local backend dev)

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

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=wsgi:app
flask run
```

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
