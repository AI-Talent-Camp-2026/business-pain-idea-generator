# Quickstart Guide: Pain-to-Idea Generator MVP

**Last updated**: 2026-02-04
**Target audience**: Developers setting up local environment

## Prerequisites

### Required Software

- **Python 3.14** (confirmed installed on Windows 10)
- **Node.js** (confirmed installed, for optional tooling)
- **Git** (for version control)
- **Redis** (for job queue)

### Required Accounts

- **OpenRouter API Key**: Get from https://openrouter.ai/keys
  - Cost estimate: $5-10 для тестирования MVP
  - Модель: Claude 3.5 Sonnet или Haiku

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd business-pain-idea-generator
git checkout 001-pain-to-idea-mvp
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Install Redis

**Option A: Redis on Windows (WSL recommended)**
```bash
# If you have WSL (Windows Subsystem for Linux)
wsl --install
wsl
sudo apt-get update
sudo apt-get install redis-server
redis-server
```

**Option B: Docker (easiest for Windows)**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Option C: Memurai (native Windows Redis)**
```powershell
# Download from https://www.memurai.com/
# Or use chocolatey
choco install memurai-developer
```

### 4. Environment Configuration

Create `.env` file in backend directory:

```env
# backend/.env
OPENROUTER_API_KEY=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
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./pain_to_idea.db
ENVIRONMENT=development
LOG_LEVEL=INFO

# Rate limiting
RATE_LIMIT_RUNS_PER_HOUR=5

# Performance targets
GENERATION_TIMEOUT_SECONDS=600  # 10 minutes (Bronze target)
```

### 5. Initialize Database

```bash
cd backend
python -m src.models.init_db
```

This creates SQLite database with schema from data-model.md.

### 6. Start Services

**Terminal 1: Redis (if not using Docker)**
```bash
redis-server
```

**Terminal 2: RQ Worker**
```bash
cd backend
python -m src.workers.run_worker
```

**Terminal 3: FastAPI Backend**
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 4: Frontend (simple HTTP server)**
```bash
cd frontend
python -m http.server 3000
```

### 7. Verify Installation

Open browser and navigate to:

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Development Workflow

### Running a Test Generation

1. Open http://localhost:3000
2. Click "Запустить прогон"
3. Optionally enter direction (e.g., "B2B SaaS")
4. Watch progress on status page
5. View results when complete

### Checking Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Worker logs
tail -f backend/logs/worker.log

# Redis queue status
redis-cli
> KEYS rq:*
> LLEN rq:queue:default
```

### Database Inspection

```bash
# SQLite CLI
sqlite3 backend/pain_to_idea.db

# Useful queries
SELECT * FROM runs ORDER BY created_at DESC LIMIT 5;
SELECT COUNT(*) FROM ideas WHERE run_id = 'your-run-id';
SELECT * FROM analogues WHERE idea_id = 1;
```

## Testing

### Manual Testing Checklist

- [ ] Can create new run via API
- [ ] Worker picks up job and starts processing
- [ ] SSE progress updates work
- [ ] Run completes with 10-20 ideas
- [ ] Each idea has 2+ analogues
- [ ] All text is in Russian
- [ ] Export to Markdown works
- [ ] Rate limiting blocks 6th request

### API Testing with curl

```bash
# Create run
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"optional_direction": "B2B SaaS"}'

# Get status (replace {run_id})
curl http://localhost:8000/api/runs/{run_id}

# Get ideas
curl http://localhost:8000/api/runs/{run_id}/ideas

# Export markdown
curl -X POST http://localhost:8000/api/export/markdown \
  -H "Content-Type: application/json" \
  -d '{"run_id": "{run_id}"}' \
  -o ideas.md
```

## Troubleshooting

### Redis Connection Error

**Error**: `redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379`

**Solution**:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not, start Redis server
redis-server
# Or via Docker
docker start <redis-container-id>
```

### OpenRouter API Error

**Error**: `401 Unauthorized`

**Solution**:
- Verify OPENROUTER_API_KEY in .env file
- Check key is valid at https://openrouter.ai/keys
- Ensure key has credits/balance

### Worker Not Processing Jobs

**Error**: Jobs stay in "pending" status forever

**Solution**:
```bash
# Check worker is running
ps aux | grep run_worker

# Restart worker
cd backend
python -m src.workers.run_worker
```

### Frontend Not Loading

**Error**: Cannot connect to http://localhost:3000

**Solution**:
```bash
# Ensure HTTP server is running
cd frontend
python -m http.server 3000

# Or use Node.js alternative
npx http-server -p 3000
```

### Database Locked Error

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
SQLite doesn't handle high concurrency well. For MVP:
```bash
# Close all connections and restart
pkill -f uvicorn
pkill -f run_worker
rm backend/pain_to_idea.db
python -m src.models.init_db
# Restart services
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| OPENROUTER_API_KEY | Yes | - | API key from OpenRouter |
| REDIS_URL | Yes | redis://localhost:6379/0 | Redis connection URL |
| DATABASE_URL | Yes | sqlite:///./pain_to_idea.db | SQLite database path |
| ENVIRONMENT | No | development | Environment name |
| LOG_LEVEL | No | INFO | Logging level |
| RATE_LIMIT_RUNS_PER_HOUR | No | 5 | Max runs per IP per hour |
| GENERATION_TIMEOUT_SECONDS | No | 600 | Max generation time (10 min) |

### FastAPI Configuration

Customize in `backend/src/config.py`:

```python
class Settings:
    app_name = "Pain-to-Idea Generator"
    version = "1.0.0"
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    redis_url = os.getenv("REDIS_URL")
    database_url = os.getenv("DATABASE_URL")
    ...
```

## Next Steps

After verifying local setup works:

1. **Review Constitution**: Read `.specify/memory/constitution.md`
2. **Check Tasks**: See `specs/001-pain-to-idea-mvp/tasks.md` (generated by speckit.tasks)
3. **Start Implementation**: Follow tasks in order
4. **Deploy**: See deployment guide in `specs/001-pain-to-idea-mvp/deployment.md`

## Support

For issues or questions:
- Check `specs/001-pain-to-idea-mvp/plan.md` for architectural decisions
- Review API contracts in `specs/001-pain-to-idea-mvp/contracts/`
- Consult lean canvas documentation in `lean_canvas/`

## Quick Reference

### Start All Services (single command)

Create `start-all.sh`:
```bash
#!/bin/bash
redis-server &
cd backend && python -m src.workers.run_worker &
cd backend && uvicorn src.main:app --reload --port 8000 &
cd frontend && python -m http.server 3000 &
echo "All services started!"
```

### Stop All Services

```bash
pkill -f redis-server
pkill -f run_worker
pkill -f uvicorn
pkill -f http.server
```

### Reset Everything

```bash
# Stop services
pkill -f redis-server
pkill -f run_worker
pkill -f uvicorn

# Clear data
rm backend/pain_to_idea.db
redis-cli FLUSHALL

# Reinitialize
cd backend
python -m src.models.init_db
```
