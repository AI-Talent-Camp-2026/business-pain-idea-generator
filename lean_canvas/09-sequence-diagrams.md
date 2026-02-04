# Sequence Diagrams: Генератор болей → бизнес-идеи

> Основано на: USM v1.0, C4 v1.0, API Inventory v1.0

## Обзор

| # | Сценарий | Сложность | Участники |
|---|----------|-----------|-----------|
| 1 | Запуск прогона и получение 10–20 идей | Высокая | Пользователь, Веб, API, Очередь, Воркеры, Источники, Поиск/тренды, LLM, БД |
| 2 | Экспорт выбранных идей | Средняя | Пользователь, Веб, API, Хранилище, БД |

---

## 1. Запуск прогона и получение 10–20 идей

### Контекст

**User Story:** US-001, US-003, US-005, US-006, US-007  
**Идея:** UI не должен “висеть”, прогон асинхронный; важны статус и прозрачность.

### Диаграмма

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as Веб‑приложение
    participant A as Backend API
    participant Q as Очередь задач
    participant X as Воркеры анализа
    participant S as Публичные источники
    participant T as Поиск/тренды
    participant L as Провайдер LLM
    participant D as База данных

    U->>W: Нажимает "Сгенерировать идеи"
    W->>A: POST /runs {ideasRequested=12, focusHint?}
    A->>D: INSERT run(status=queued)
    A-)Q: enqueue(runId)
    A-->>W: 202 Accepted {runId}
    W-->>U: Переходит на экран статуса

    loop Пока статус != succeeded/failed
        W->>A: GET /runs/{runId}/status
        A->>D: SELECT run.status + progress
        A-->>W: status/progress
        W-->>U: Обновляет прогресс
    end

    Q--)X: deliver job(runId)
    activate X

    X->>D: UPDATE run(status=running)
    X->>S: Сбор сигналов (по источникам)
    S-->>X: Посты/комментарии/метаданные
    X->>T: Поиск аналогов/контекста (опц.)
    T-->>X: Ссылки/сниппеты

    X->>L: Кластеризация болей + формулировки (RU)
    L-->>X: pain_points + evidences (структурировано)
    X->>D: INSERT pain_points + evidences

    X->>L: Генерация 10–20 идей на основе болей (RU)
    L-->>X: ideas + analogs + plan drafts
    X->>D: INSERT ideas + analogs + plans

    alt Всё ок
        X->>D: UPDATE run(status=succeeded, ideas_generated=N)
    else Ошибка источников/моделей
        X->>D: UPDATE run(status=failed, error_summary)
        X->>D: INSERT run_event(type=error, message)
    end
    deactivate X

    W->>A: GET /runs/{runId}/ideas
    A->>D: SELECT ideas + analogs + plans
    A-->>W: results
    W-->>U: Показывает список 10–20 идей
```

### Примечания

- Прогресс лучше считать по этапам: “сбор сигналов → формулировка болей → генерация идей → аналоги → план”.
- При деградации качества важно честно помечать: “аналоги требуют проверки / источники недоступны”.

---

## 2. Экспорт выбранных идей

### Контекст

**User Story:** US-010  
**Цель:** быстро получить документ/таблицу/ссылку для обсуждения.

### Диаграмма

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as Веб‑приложение
    participant A as Backend API
    participant D as База данных
    participant F as Хранилище/артефакты

    U->>W: Выбирает 1–2 идеи и нажимает "Экспорт"
    W->>A: POST /exports {ideaIds, format}
    A->>D: SELECT ideas + analogs + plans
    A->>F: Create export artifact (doc/table/link)
    F-->>A: export_url
    A->>D: INSERT export(export_url, format)
    A-->>W: 201 Created {exportId, export_url}
    W-->>U: Показывает ссылку/скачивание
```

---

## 3. “Подробнее” по доказательствам (по кнопке на странице идеи)

### Контекст

**User Story:** US-005 (режим “не перегружать” + детали по запросу)  
**Цель:** по умолчанию показывать только паттерны, а ссылки/цитаты/обсуждения — по явному действию.

### Диаграмма

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant W as Веб‑приложение
    participant A as Backend API
    participant D as База данных

    U->>W: Нажимает "Подробнее" в блоке сигналов
    W->>A: GET /ideas/{ideaId}/evidence
    A->>D: SELECT evidences + source URLs
    A-->>W: links + (опц.) обезличенные цитаты
    W-->>U: Показывает боковую панель/модал
```

---

## Приложения

### Участники (из C4)

| ID | Название | Тип | Описание |
|----|----------|-----|----------|
| W | Веб‑приложение | Container | UI на русском |
| A | Backend API | Container | Оркестрация и данные |
| Q | Очередь | Container | Асинхронные задачи |
| X | Воркеры | Container | Анализ и генерация |
| S/T/L | Внешние | System_Ext | Источники/поиск/LLM |

### Соглашения

- `->>` / `-->>` — синхронные
- `-)` / `--)` — асинхронные
- `alt/else` — ветвления ошибок
