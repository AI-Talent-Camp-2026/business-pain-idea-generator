# Интеграция с Tavily Search API

## Что изменилось?

Теперь приложение **ДЕЙСТВИТЕЛЬНО ищет реальные боли пользователей** из интернета, а не просто генерирует их через LLM!

### До интеграции:
```
Пользователь → Claude придумывает боли из головы → Идеи
```

### После интеграции:
```
Пользователь →
  1. Tavily ищет реальные обсуждения (Reddit, Indie Hackers, форумы) →
  2. Claude анализирует находки и извлекает боли →
  3. Claude генерирует идеи на основе РЕАЛЬНЫХ данных →
Идеи
```

---

## Архитектура

### 1. **TavilyScraper** (`backend/src/scrapers/tavily_scraper.py`)
- Использует Tavily Search API для поиска обсуждений
- Ищет по keywords: "problem", "pain", "frustrating", "need solution"
- Фокусируется на: Reddit, Indie Hackers, Hacker News, ProductHunt
- Возвращает релевантные отрывки текста с URL источников

### 2. **PainAnalyzer** (`backend/src/llm/pain_analyzer.py`)
- Получает сырые тексты от Tavily
- Использует Claude для извлечения структурированных болей
- Группирует похожие боли
- Оценивает уровень уверенности (high/medium/low) на основе количества доказательств

### 3. **Generation Pipeline** (`backend/src/workers/generation_pipeline.py`)
- **Stage 1**: Поиск через Tavily (10+ результатов)
- **Stage 2**: Анализ и извлечение болей через Claude
- **Stage 3**: Генерация идей на основе реальных данных

---

## Настройка

### 1. Tavily API Key

Уже добавлен в `backend/.env`:
```env
TAVILY_API_KEY=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
```

**Бесплатный план**: 1000 запросов/месяц

### 2. Зависимости

Не требуется дополнительных библиотек - используется уже установленный `httpx`.

---

## Как это работает?

### Пример запроса:

**Направление:** "B2B SaaS для стартапов"

#### Этап 1: Tavily Search
```python
# Формируются 3 поисковых запроса:
1. "b2b saas стартапы problem struggle pain site:reddit.com OR site:indiehackers.com"
2. "b2b saas стартапы frustrating annoying difficult site:reddit.com OR site:indiehackers.com"
3. "b2b saas стартапы need solution site:reddit.com OR site:indiehackers.com"

# Результаты (пример):
[
  {
    "title": "Managing invoices for my SaaS is killing me",
    "content": "I spend 5+ hours every week manually creating invoices...",
    "url": "reddit.com/r/Entrepreneur/...",
    "source": "reddit.com"
  },
  ...
]
```

#### Этап 2: Pain Analysis
```python
# Claude анализирует тексты и извлекает:
[
  {
    "pain_description": "Ручное создание счетов отнимает 5+ часов в неделю у B2B SaaS фаундеров",
    "segment": "B2B SaaS фаундеры с менее чем 50 клиентами",
    "evidence_quotes": [
      "I spend 5+ hours every week manually creating invoices",
      "Invoice management is my biggest time sink"
    ],
    "confidence_level": "high"  # Много подтверждений
  }
]
```

#### Этап 3: Idea Generation
```python
# Claude получает РЕАЛЬНЫЕ боли и генерирует идеи:
{
  "title": "InvoiceAutomate - автоматизация счетов для B2B SaaS",
  "pain_description": "Ручное создание счетов отнимает 5+ часов...",  # ИЗ РЕАЛЬНЫХ ДАННЫХ
  "brief_evidence": "\"I spend 5+ hours every week...\"",  # ЦИТАТЫ ИЗ REDDIT
  "confidence_level": "high",  # ИЗ АНАЛИЗА
  ...
}
```

---

## Преимущества

### 1. **Реальные данные**
- Боли извлекаются из реальных обсуждений
- Каждая боль имеет цитаты-доказательства
- URL источников для проверки

### 2. **Высокая релевантность**
- Tavily специально создан для AI-поиска
- Фокус на качественных источниках (Reddit, IH, HN)
- Фильтрация по keywords болей

### 3. **Оценка уверенности**
- High: много подтверждений из разных источников
- Medium: несколько упоминаний
- Low: единичные упоминания

### 4. **Прозрачность**
- Все цитаты сохраняются в `brief_evidence`
- Можно проверить источники по URL
- Ясно видно, откуда взялась каждая боль

---

## Логирование

В процессе генерации вы увидите:

```
[Tavily] Searching for pains in direction: B2B SaaS для стартапов
[Tavily] Query 'b2b saas problem...' returned 8 results
[Tavily] Total unique results: 15

[PainAnalyzer] Analyzing 15 search results
[PainAnalyzer] Processing batch 1/1
[PainAnalyzer] Extracted 5 unique pains

[Stage 3] Using REAL PAINS mode with 5 pains
```

---

## Fallback режим

Если Tavily не находит достаточно данных (< 3 болей):
- Система автоматически переключается на LLM-only режим
- Генерация продолжится как раньше
- В логах будет: `[Stage 3] Falling back to LLM-only mode`

---

## Лимиты Tavily

**Бесплатный план:**
- 1000 запросов/месяц
- ~3 запроса на 1 генерацию идей
- **~333 генерации в месяц**

**Оптимизация:**
- Результаты кэшируются в рамках одного прогона
- Используется `max_results=10` вместо 100

---

## Тестирование

Запустите генерацию и проверьте логи:

```bash
cd backend
python -m src.workers.run_worker
```

В другом терминале:
```bash
curl -X POST http://localhost:8000/api/runs
```

Смотрите логи - должны увидеть все 3 этапа работы.

---

## Что дальше?

### Возможные улучшения:

1. **Кэширование результатов Tavily**
   - Сохранять результаты поиска в Redis на 24 часа
   - Экономия API запросов

2. **Больше источников**
   - Twitter/X через Tavily
   - Quora
   - LinkedIn discussions

3. **Semantic clustering**
   - Группировка похожих болей через embeddings
   - Удаление дубликатов

4. **Показывать источники в UI**
   - Добавить ссылки на оригинальные обсуждения
   - "Боль подтверждена 15 обсуждениями на Reddit"

---

## Поддержка

Если что-то не работает:

1. Проверьте TAVILY_API_KEY в `.env`
2. Проверьте логи: `backend/logs/app.log`
3. Убедитесь что Redis запущен
4. Проверьте лимиты Tavily: https://tavily.com/dashboard

---

**Статус:** ✅ Интеграция завершена и готова к использованию!
