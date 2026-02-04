# API Inventory: Генератор болей → бизнес-идеи

> Основано на: USM v1.0  
> Базовый URL: `https://api.example.com/v1`

## Обзор

**Всего endpoints (оценка, Day‑1):** 3–6  
**API Style:** REST  
**Формат:** JSON  
**Авторизация (Day‑1):** нет end‑user auth. Опционально: общий `X-Access-Key` для демо/кемпа (анти‑абьюз).

### Сводка по доменам

| Домен | Endpoints | Описание |
|-------|-----------|----------|
| Runs | 2–3 | запуск, статус, результат |
| Exports | 0–1 | (опционально) серверный export в Markdown |

---

## 1. Runs (прогоны) — Day‑1

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /runs | Public* | Запустить новый прогон (10–20 идей) |
| GET | /runs/{runId}/status | Public* | Статус/прогресс |
| GET | /runs/{runId}/result | Public* | Итоговый idea pack (включая аналоги и план/сроки) |

### `POST /runs`

**Назначение:** Запуск прогона  
**User Story:** US-001, US-002, US-003  
**Авторизация:** Public*  
*\*Опционально требовать `X-Access-Key` для демо/кемпа.*

**Request Body:**
- focusHint? (string, optional)
- ideasRequested (int, default 12; range 10–20)

**Responses:**
- `202` — принято, возвращает runId и статус queued
- `400` — неверные параметры
- `429` — лимит прогонов/скорость

---

## 2. Результат и “Подробнее” (Day‑1 упрощение)

В Day‑1 **не дробим на отдельные endpoints** `/ideas/*`. Данные для экрана “Детали идеи” приходят в составе `GET /runs/{runId}/result`.

- **По умолчанию UI показывает** короткие паттерны/сигналы (2–5 строк).
- По клику “Подробнее” UI раскрывает **уже полученные** ссылки/примеры (без отдельного API‑запроса).  
  (Оптимизация “лениво догружать evidence отдельным запросом” — после MVP.)

---

## 3. Exports (экспорт) — опционально в Day‑1

Рекомендуемый Day‑1 вариант: **экспорт формируется на клиенте** (копировать Markdown / скачать файл) без API.

Если всё-таки нужен серверный экспорт:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /runs/{runId}/export?format=md | Public* | Markdown для копирования/скачивания |

---

## После Day‑1 (вне 1‑day MVP)

- Auth (регистрация/логин/профиль), Favorites, Library, Search, Admin, история экспортов.
- Дробление результата на отдельные ресурсы (`/ideas/{id}/evidence`, `/analogs`, `/plan`) — оптимизация после MVP.

---

## Приложения

### Коды ошибок

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Business error |
| 429 | Rate limit |
| 500 | Internal error |

### Формат ошибки

`{ "error": { "code": "...", "message": "...", "details": [...] } }`

### Пагинация

`?page=N&limit=N`  
Response: `{ "pagination": { "page", "limit", "total", "pages" } }`
