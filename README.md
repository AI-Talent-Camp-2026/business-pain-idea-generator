# Pain-to-Idea Generator MVP

Генератор бизнес-идей из реальных пользовательских болей.

## 📊 Статус проекта

### ✅ Завершено:

1. **Архитектурная документация** (100%):
   - [Constitution](\.specify\memory\constitution.md) - принципы проекта
   - [Specification](specs\001-pain-to-idea-mvp\spec.md) - 5 user stories, 18 требований
   - [Implementation Plan](specs\001-pain-to-idea-mvp\plan.md) - технический план
   - [Data Model](specs\001-pain-to-idea-mvp\data-model.md) - схема БД
   - [API Contracts](specs\001-pain-to-idea-mvp\contracts\openapi.yaml) - спецификация API
   - [Tasks](specs\001-pain-to-idea-mvp\tasks.md) - 77 задач для реализации

2. **Инфраструктура** (60%):
   - ✅ Структура проекта (backend + frontend)
   - ✅ .gitignore
   - ✅ requirements.txt
   - ✅ .env.example
   - ✅ Database models (SQLAlchemy): Run, Idea, Analogue, Evidence
   - ✅ LLM client (OpenRouter)
   - ✅ Russian prompts
   - ✅ Frontend JavaScript (app.js, api.js)

### 🚧 Требуется завершить:

#### Backend (осталось ~4-5 часов работы):

1. **FastAPI application** (`backend/src/main.py`):
   ```python
   # Создать FastAPI app с CORS
   # Подключить роуты
   # Настроить rate limiting
   # Добавить health endpoint
   ```

2. **API Routes**:
   - `backend/src/api/runs.py` - POST /api/runs, GET /api/runs/{id}
   - `backend/src/api/ideas.py` - GET /api/runs/{id}/ideas, GET /api/ideas/{id}

3. **Services**:
   - `backend/src/services/run_service.py` - создание и управление прогонами
   - `backend/src/services/idea_service.py` - получение идей

4. **Workers** (критический компонент):
   - `backend/src/workers/generation_pipeline.py` - генерация идей через OpenRouter
   - `backend/src/workers/run_worker.py` - RQ worker для обработки задач

#### Frontend (осталось ~2-3 часа работы):

1. **HTML страницы** (используя app.js который уже готов):
   - `frontend/index.html` - главная страница + запуск
   - `frontend/status.html` - отслеживание прогресса
   - `frontend/results.html` - список идей
   - `frontend/detail.html` - детали идеи

2. **Стилизация** (опционально):
   - Базовый CSS или TailwindCSS CDN

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Установить Playwright browsers (для scraping)
playwright install
```

### 2. Настройка окружения

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

### 3. Установка Redis

**Windows (Docker)**:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Или Windows (Memurai)**:
```powershell
choco install memurai-developer
```

### 4. Инициализация БД

```bash
cd backend
python -m src.models.init_db
```

### 5. Запуск сервисов

**Terminal 1: Backend**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 2: Worker** (после создания run_worker.py):
```bash
cd backend
python -m src.workers.run_worker
```

**Terminal 3: Frontend**:
```bash
cd frontend
python -m http.server 3000
```

## 📝 Следующие шаги для завершения MVP

### Вариант 1: Автоматизированная генерация (рекомендуется)

Запустите Claude Code для завершения реализации:

1. Откройте проект в Claude Code
2. Выполните команду: `/speckit.implement` для продолжения реализации
3. Выберите критический путь (User Stories 1, 3, 4 + Workers)

### Вариант 2: Ручная реализация

Следуйте списку задач из [tasks.md](specs\001-pain-to-idea-mvp\tasks.md):

**Приоритет 1 (критический путь)**:
- [ ] T014-T018: FastAPI app setup
- [ ] T019-T024: User Story 1 (Start Run)
- [ ] T031-T037: User Story 3 (View Ideas)
- [ ] T038-T043: User Story 4 (View Details)
- [ ] T051-T064: Workers Pipeline

**Приоритет 2 (улучшения)**:
- [ ] T025-T030: User Story 2 (Progress tracking с polling)
- [ ] T065-T077: Polish (error handling, logging, styling)

## 📚 Документация

- **Quickstart**: [specs/001-pain-to-idea-mvp/quickstart.md](specs\001-pain-to-idea-mvp\quickstart.md)
- **API Spec**: [specs/001-pain-to-idea-mvp/contracts/openapi.yaml](specs\001-pain-to-idea-mvp\contracts\openapi.yaml)
- **Constitution**: [.specify/memory/constitution.md](.specify\memory\constitution.md)

## 🎯 Ожидаемый результат

После завершения реализации вы получите:

1. **Работающий веб-интерфейс** на русском языке
2. **Генерация 10-15 бизнес-идей** через OpenRouter (Claude)
3. **Полные idea packs**: боль + аналоги + планы 7/30 дней
4. **Асинхронная обработка** через Redis + RQ workers
5. **SQLite БД** с 24-часовым хранением
6. **Rate limiting** для защиты от злоупотреблений

## 🛠️ Технический стек

- **Backend**: Python 3.14, FastAPI, SQLAlchemy, RQ
- **Frontend**: Vanilla JS, HTML5, CSS
- **Database**: SQLite
- **Queue**: Redis + Python-RQ
- **LLM**: OpenRouter (Claude 3.5 Sonnet)
- **Deployment**: Railway/Render/Fly.io

## 📞 Помощь

Если нужна помощь с завершением реализации:

1. Проверьте [troubleshooting](specs\001-pain-to-idea-mvp\quickstart.md#troubleshooting) в quickstart.md
2. Убедитесь что Redis запущен: `redis-cli ping`
3. Проверьте логи: `backend/logs/app.log`
4. Изучите [tasks.md](specs\001-pain-to-idea-mvp\tasks.md) для пошагового плана

## ⏱️ Оценка времени до запуска

- **Минимальный прототип** (без scraping, упрощенная генерация): 2-3 часа
- **Полный MVP** (все User Stories 1-4): 6-8 часов
- **Production-ready** (с тестами, мониторингом): 12-16 часов

Текущий прогресс: **~40% готово** (архитектура + база + клиенты)
