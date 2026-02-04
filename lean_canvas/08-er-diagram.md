# Data Model: Генератор болей → бизнес-идеи

> Версия: 1.0  
> Основано на: Brief v1.0, USM v1.0  

## 1. Обзор

**Всего сущностей (ядро):** ~12 (без справочников)  
**Тип хранения:** SQL‑модель (концептуально)

### Группы
- **Core:** users, sessions (опционально), user_settings
- **Runs:** runs, run_events, run_sources
- **Insights:** pain_points, evidences
- **Ideas:** ideas, idea_analogs, idea_plans
- **User actions:** favorites, exports
- **Reference:** tags (опционально)

## 2. ER-диаграмма

```mermaid
erDiagram
    users {
        uuid id PK
        string email UK
        string password_hash
        string display_name
        string role "user/admin"
        timestamp created_at
        timestamp last_login_at
    }

    runs {
        uuid id PK
        uuid user_id FK
        string focus_hint "опциональный фокус"
        string status "queued/running/succeeded/failed"
        int ideas_requested "10-20"
        int ideas_generated
        string confidence_note "сводка уверенности"
        timestamp started_at
        timestamp finished_at
        timestamp created_at
    }

    run_events {
        uuid id PK
        uuid run_id FK
        string type "progress/error/info"
        string message
        timestamp created_at
    }

    run_sources {
        uuid id PK
        uuid run_id FK
        string source_type "forums/trends/reviews/etc"
        string source_label
        string source_url
        timestamp created_at
    }

    pain_points {
        uuid id PK
        uuid run_id FK
        string title
        text description
        string audience_segment
        string severity "low/medium/high"
        string confidence "low/medium/high"
        timestamp created_at
    }

    evidences {
        uuid id PK
        uuid pain_point_id FK
        string evidence_type "phrase/pattern/link"
        text evidence_text
        string source_url
        timestamp created_at
    }

    ideas {
        uuid id PK
        uuid run_id FK
        uuid pain_point_id FK
        string title
        text problem_statement
        text solution_hypothesis
        string target_customer
        string confidence "low/medium/high"
        string time_to_mvp "7d/30d (90d optional позже)"
        timestamp created_at
    }

    idea_analogs {
        uuid id PK
        uuid idea_id FK
        string name
        string url
        text note
        string status "active/unknown/closed"
        timestamp created_at
    }

    idea_plans {
        uuid id PK
        uuid idea_id FK
        string plan_variant "7d/30d"
        text plan_steps
        string timeline_summary
        timestamp created_at
    }

    favorites {
        uuid id PK
        uuid user_id FK
        uuid idea_id FK
        timestamp created_at
    }

    exports {
        uuid id PK
        uuid user_id FK
        uuid run_id FK
        string format "doc/table/link"
        string export_url
        timestamp created_at
    }

    users ||--o{ runs : "starts"
    runs ||--o{ run_events : "logs"
    runs ||--o{ run_sources : "uses"
    runs ||--o{ pain_points : "extracts"
    pain_points ||--o{ evidences : "supported_by"
    runs ||--o{ ideas : "generates"
    pain_points ||--o{ ideas : "inspires"
    ideas ||--o{ idea_analogs : "has"
    ideas ||--o{ idea_plans : "has"
    users ||--o{ favorites : "saves"
    ideas ||--o{ favorites : "favorited"
    users ||--o{ exports : "exports"
    runs ||--o{ exports : "exported"
```

## 3. Описание сущностей (коротко)

### `runs`
**Назначение:** единица “прогона” генерации. Хранит статус, фокус, метрики результата.

### `pain_points` + `evidences`
**Назначение:** боли и их “обоснования” (для доверия и прозрачности).

### `ideas` + `idea_analogs` + `idea_plans`
**Назначение:** итоговые бизнес‑идеи, аналоги с ссылками и план/сроки.

## 4. Связи

| Связь | Тип | Описание | Каскад |
|-------|-----|----------|--------|
| users → runs | 1:N | пользователь запускает прогоны | удалить прогон при удалении пользователя (по политике) |
| runs → pain_points | 1:N | прогон извлекает боли | да |
| pain_points → evidences | 1:N | доказательства боли | да |
| runs → ideas | 1:N | прогон генерирует идеи | да |
| ideas → analogs/plans | 1:N | детали идеи | да |

## 5. Миграции (порядок)

1. users
2. runs
3. pain_points, evidences
4. ideas, idea_analogs, idea_plans
5. favorites, exports
