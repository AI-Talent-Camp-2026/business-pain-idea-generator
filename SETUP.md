# Инструкция по установке и запуску MVP

## Текущий статус

✅ **Готово к запуску** (~40%):
- Структура проекта
- Database models
- LLM client + prompts
- Frontend JavaScript

🚧 **Требует завершения** (~60%):
- FastAPI routes
- Workers pipeline
- HTML страницы

## Пошаговая установка

### Шаг 1: Клонирование и зависимости

```bash
# Перейти в директорию проекта
cd c:\wwwork\business-pain-idea-generator

# Создать виртуальное окружение
cd backend
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Установить Playwright browsers
playwright install chromium
```

### Шаг 2: Redis

**Вариант A - Docker (рекомендуется)**:
```bash
docker run -d --name redis-pain-to-idea -p 6379:6379 redis:7-alpine
```

**Вариант B - Memurai (Windows native)**:
1. Скачать с https://www.memurai.com/
2. Установить
3. Запустить Memurai Service

**Проверка**:
```bash
redis-cli ping
# Ответ должен быть: PONG
```

### Шаг 3: Конфигурация

Создать `backend/.env`:
```env
OPENROUTER_API_KEY=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
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./pain_to_idea.db
ENVIRONMENT=development
LOG_LEVEL=INFO
RATE_LIMIT_RUNS_PER_HOUR=5
GENERATION_TIMEOUT_SECONDS=600
```

### Шаг 4: Инициализация БД

```bash
cd backend
python -m src.models.init_db
```

Должно появиться сообщение: `Database tables created successfully!`

### Шаг 5: Завершение реализации

Для завершения MVP нужно создать оставшиеся файлы. Два варианта:

#### Вариант A: Использовать Claude Code (быстрее)

```bash
# В Claude Code выполнить
/speckit.implement

# Выбрать "Continue implementation"
# Указать критический путь: US1, US3, US4 + Workers
```

#### Вариант B: Создать вручную (см. ниже)

---

## Ручное завершение (если выбран вариант B)

### Файлы для создания:

#### 1. `backend/src/main.py` - FastAPI App

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .api import runs, ideas

app = FastAPI(title=settings.app_name, version=settings.version)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routers
app.include_router(runs.router, prefix="/api", tags=["runs"])
app.include_router(ideas.router, prefix="/api", tags=["ideas"])
```

#### 2. `backend/src/api/runs.py` - Runs API

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from ..models import get_db, Run
from ..services.run_service import create_run, get_run_status

router = APIRouter()

class CreateRunRequest(BaseModel):
    optional_direction: Optional[str] = None

@router.post("/runs")
async def create_new_run(request: CreateRunRequest, db: Session = Depends(get_db)):
    run = create_run(db, request.optional_direction)
    return {"run_id": run.id, "status": run.status, "created_at": run.created_at.isoformat()}

@router.get("/runs/{run_id}")
async def get_run(run_id: str, db: Session = Depends(get_db)):
    run = get_run_status(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Прогон не найден")
    return run.to_dict()
```

#### 3. `backend/src/services/run_service.py` - Run Service

```python
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue
import uuid

from ..models import Run
from ..config import settings

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue(connection=redis_conn)

def create_run(db: Session, optional_direction: str = None):
    run = Run(
        id=str(uuid.uuid4()),
        optional_direction=optional_direction,
        status='pending'
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Enqueue worker job
    from ..workers.generation_pipeline import generate_ideas
    queue.enqueue(generate_ideas, run.id, job_timeout=settings.generation_timeout_seconds)

    return run

def get_run_status(db: Session, run_id: str):
    return db.query(Run).filter(Run.id == run_id).first()
```

#### 4. `backend/src/workers/generation_pipeline.py` - Worker

```python
from sqlalchemy.orm import Session
from ..models import SessionLocal, Run, Idea, Analogue
from ..llm.client import llm_client
from ..llm.prompts import get_generate_ideas_prompt, SYSTEM_PROMPT
from ..config import logger
import json
from datetime import datetime

def generate_ideas(run_id: str):
    db = SessionLocal()
    try:
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            return

        run.status = 'running'
        run.current_stage = 'Генерация идей'
        db.commit()

        # Generate via LLM
        prompt = get_generate_ideas_prompt(run.optional_direction or "")
        response = llm_client.generate(prompt, SYSTEM_PROMPT)

        # Parse JSON
        ideas_data = json.loads(response)

        # Save to database
        for idx, idea_data in enumerate(ideas_data.get('ideas', [])[:15]):
            idea = Idea(
                run_id=run_id,
                title=idea_data['title'],
                pain_description=idea_data['pain_description'],
                segment=idea_data['segment'],
                confidence_level=idea_data['confidence_level'],
                brief_evidence=idea_data.get('brief_evidence', 'Доказательства генерируются...'),
                plan_7days=idea_data.get('plan_7days', 'План на 7 дней...'),
                plan_30days=idea_data.get('plan_30days', 'План на 30 дней...'),
                order_index=idx
            )
            db.add(idea)
            db.flush()

            # Add analogues
            for aidx, analogue_data in enumerate(idea_data.get('analogues', [])[:3]):
                analogue = Analogue(
                    idea_id=idea.id,
                    name=analogue_data['name'],
                    description=analogue_data['description'],
                    url=analogue_data['url'],
                    order_index=aidx
                )
                db.add(analogue)

        run.status = 'completed'
        run.completed_at = datetime.utcnow()
        run.ideas_count = len(ideas_data.get('ideas', []))
        db.commit()

    except Exception as e:
        logger.error(f"Error in generation pipeline: {e}")
        run.status = 'failed'
        run.error_message = f"Ошибка генерации: {str(e)}"
        db.commit()
    finally:
        db.close()
```

#### 5. HTML страницы (примеры в след. секции)

---

## Запуск после завершения

```bash
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload --port 8000

# Terminal 2: Worker
cd backend
python -m src.workers.run_worker

# Terminal 3: Frontend
cd frontend
python -m http.server 3000
```

Открыть: http://localhost:3000

---

## Минимальный тест

```bash
# Создать прогон
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"optional_direction": "B2B SaaS"}'

# Получить статус (замените {run_id})
curl http://localhost:8000/api/runs/{run_id}

# Дождаться статуса "completed" (до 3-5 минут)
# Получить идеи
curl http://localhost:8000/api/runs/{run_id}/ideas
```

---

## Troubleshooting

### Redis не запускается
```bash
# Проверить порт
netstat -an | findstr 6379

# Убить процесс на порту
taskkill /PID <PID> /F

# Перезапустить Redis
docker restart redis-pain-to-idea
```

### OpenRouter API error 401
- Проверить `.env` файл
- Убедиться что ключ активен на https://openrouter.ai/keys

### Worker не подхватывает задачи
```bash
# Проверить очередь
redis-cli
> KEYS rq:*
> LLEN rq:queue:default

# Если задачи висят - перезапустить worker
```

### База данных locked
```bash
# Закрыть все соединения
taskkill /F /IM python.exe

# Удалить БД и пересоздать
rm backend/pain_to_idea.db
python -m src.models.init_db
```

---

## Следующие шаги

После завершения базового MVP:

1. ✅ Протестировать core flow end-to-end
2. ➕ Добавить User Story 2 (Progress tracking)
3. ➕ Добавить User Story 5 (Export to Markdown)
4. 🎨 Улучшить стилизацию (TailwindCSS)
5. 📊 Добавить логирование и мониторинг
6. 🚀 Задеплоить на Railway/Render

---

**Время до первого запуска**: 2-4 часа (при ручной реализации)
**Текущий прогресс**: 40% готово
