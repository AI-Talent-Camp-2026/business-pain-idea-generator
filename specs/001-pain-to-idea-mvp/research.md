# Research: Pain-to-Idea Generator MVP

**Date**: 2026-02-04
**Feature**: 001-pain-to-idea-mvp
**Purpose**: Technical research and technology decisions for 1-day MVP

## Research Questions Addressed

### 1. Technology Stack for 1-Day MVP

**Decision**: Python FastAPI (backend) + vanilla HTML/CSS/JS (frontend)

**Rationale**:
- **Speed to market**: Python allows rapid prototyping with minimal boilerplate
- **FastAPI advantages**: Built-in async support (critical for Principle III), automatic OpenAPI docs, minimal setup
- **No frontend framework**: Vanilla JS avoids build tooling overhead, perfect for 1-day timeline
- **Constitution compliance**: Supports all 5 core principles without complexity

**Alternatives considered**:
- **Node.js + Express**: Considered but Python ecosystem better for AI/LLM integrations
- **Django**: Too heavy for MVP, more setup overhead than FastAPI
- **React/Vue**: Build tooling would consume too much of 1-day budget

### 2. Job Queue for Async Generation

**Decision**: Python RQ (Redis Queue) with Redis

**Rationale**:
- **Simplicity**: RQ is Python-native, minimal API, perfect for MVP
- **Redis availability**: Redis can be run locally or via free tier (Upstash, Redis Cloud)
- **Constitution compliance**: Supports Principle III (async) with transparent job status
- **1-day feasibility**: Can be set up in <30 minutes

**Alternatives considered**:
- **Celery**: More powerful but significantly more complex configuration
- **Background tasks (FastAPI)**: Too simple, no persistence if process dies
- **AWS SQS**: Requires AWS account, not free for local development

### 3. Database for MVP

**Decision**: SQLite

**Rationale**:
- **Zero setup**: File-based, no server required
- **Sufficient for MVP**: Handles 50 concurrent users easily (per NFR)
- **24-hour retention**: Perfect for MVP scope (no need for production DB)
- **1-day feasibility**: No configuration, works immediately

**Alternatives considered**:
- **PostgreSQL**: Overkill for MVP, requires server setup
- **In-memory only**: Violates FR-015 (24-hour retention)
- **MongoDB**: Unnecessary complexity for structured data

### 4. Frontend UI Framework Decision

**Decision**: Vanilla HTML5 + TailwindCSS (via CDN) + Alpine.js (optional)

**Rationale**:
- **No build step**: TailwindCSS via CDN, no npm/webpack
- **Russian language**: Simple template strings, no i18n library needed
- **Rapid styling**: TailwindCSS utility classes accelerate UI development
- **Alpine.js (optional)**: Lightweight reactivity for progress updates (~15KB)

**Alternatives considered**:
- **Bootstrap**: Considered but Tailwind more flexible for custom designs
- **Pure CSS**: Too slow for polished UI in 1 day
- **React**: Build tooling overhead unacceptable for 1-day MVP

### 5. LLM Integration Strategy

**Decision**: Direct OpenRouter API calls via httpx library

**Rationale**:
- **Constitution requirement**: OpenRouter only (Principle V, MVP Constraints)
- **httpx advantages**: Async-native, cleaner than requests
- **No SDK overhead**: Direct REST calls, full control
- **Cost tracking**: Easy to log and monitor usage

**Alternatives considered**:
- **LangChain**: Too heavy, adds unnecessary abstraction layer
- **OpenAI SDK with base_url**: Works but httpx more explicit
- **Anthropic SDK**: Not applicable (OpenRouter is the gateway)

### 6. Data Scraping for Public Sources

**Decision**: Playwright + BeautifulSoup4

**Rationale**:
- **Playwright**: Handles JavaScript-heavy sites (Reddit, forums)
- **BeautifulSoup4**: Fast HTML parsing for static content
- **Hybrid approach**: Use Playwright only when needed, BS4 for speed
- **Ethics**: Public data only, respects robots.txt

**Alternatives considered**:
- **Selenium**: Slower and more resource-heavy than Playwright
- **Scrapy**: Full framework overkill for MVP
- **API-only**: Limited sources, misses many communities

### 7. Progress Tracking Implementation

**Decision**: Server-Sent Events (SSE) via FastAPI

**Rationale**:
- **Real-time updates**: Push-based, no polling overhead
- **Native browser support**: No WebSocket library needed
- **FastAPI SSE**: Built-in via `StreamingResponse`
- **Simple client**: `EventSource` API works in all modern browsers

**Alternatives considered**:
- **WebSockets**: Overkill for one-way communication
- **Polling**: Inefficient, increases server load
- **Long polling**: More complex than SSE, no advantages

### 8. Deployment Strategy for MVP

**Decision**: Single server deployment (Railway, Render, or Fly.io free tier)

**Rationale**:
- **1-day constraint**: No time for complex multi-service orchestration
- **Free hosting**: All three platforms offer free tiers sufficient for MVP
- **Integrated Redis**: Railway and Render provide Redis add-ons
- **Zero DevOps**: Git push to deploy, no Kubernetes/Docker Compose complexity

**Alternatives considered**:
- **Vercel/Netlify**: Frontend-focused, not suitable for background workers
- **Heroku**: No longer offers free tier
- **Self-hosted VPS**: Requires manual setup and maintenance

### 9. Rate Limiting Strategy

**Decision**: slowapi library (IP-based rate limiting)

**Rationale**:
- **FastAPI integration**: Decorator-based, minimal code
- **IP-based**: Sufficient for MVP without authentication
- **Configurable limits**: Easy to adjust (e.g., 5 runs per IP per hour)
- **Redis-backed**: Reuses existing Redis instance

**Alternatives considered**:
- **FastAPI-Limiter**: Similar but slowapi more actively maintained
- **Manual implementation**: Error-prone, reinvents wheel
- **Cloud WAF**: Overkill and costs money for MVP

### 10. Export to Markdown

**Decision**: Python-Markdown library with custom templates

**Rationale**:
- **Template-based**: Easy to format idea pack structure
- **Native Python**: No external dependencies beyond library
- **Readable output**: Generates clean, well-structured .md files

**Alternatives considered**:
- **Manual string concatenation**: Error-prone, hard to maintain
- **Jinja2 templates**: Works but Python-Markdown simpler for this use case

## Architecture Decisions

### Project Structure

```
backend/
├── src/
│   ├── api/           # FastAPI routes
│   ├── models/        # SQLAlchemy models
│   ├── services/      # Business logic
│   ├── workers/       # RQ job workers
│   ├── llm/           # OpenRouter integration
│   └── scrapers/      # Public source scrapers
├── tests/
└── main.py

frontend/
├── index.html         # Landing + start run
├── status.html        # Progress tracking
├── results.html       # Ideas list
├── detail.html        # Idea details
└── assets/
    ├── app.js         # Vanilla JS
    └── styles.css     # Custom styles (if needed)
```

### Data Flow

1. **User initiates run** → FastAPI creates Run record → Enqueues job to RQ
2. **Worker picks up job** → Executes stages (scraping, LLM calls) → Updates Run status
3. **Client polls/SSE** → Gets progress updates → Redirects when complete
4. **User views results** → FastAPI serves ideas from SQLite
5. **User exports** → FastAPI generates Markdown → Returns file

### LLM Prompting Strategy

**For each stage, use structured prompts in Russian**:

1. **Signal extraction**: "Проанализируй обсуждения и найди паттерны болей..."
2. **Pain clustering**: "Сгруппируй похожие боли и выдели топ-15..."
3. **Idea generation**: "Для каждой боли предложи бизнес-решение..."
4. **Analogue search**: "Найди 2-3 существующих решения для..."
5. **Plan creation**: "Создай план реализации на 7 и 30 дней для..."

**Output format**: JSON for structured data, markdown for human-readable

## Performance Optimizations for MVP

### Must-Have (to hit Bronze target: 10 min)

1. **Parallel LLM calls**: Use asyncio.gather for independent requests
2. **Smart caching**: Cache analogue searches (same products appear often)
3. **Limit scraping depth**: Max 50 posts per source
4. **Timeout handling**: 30s timeout per LLM call, retry once

### Nice-to-Have (stretch goal: Silver target: 3 min)

1. **Batch LLM requests**: Combine multiple prompts where possible
2. **Pre-scraped signals**: Maintain a rotating cache of recent discussions
3. **Faster model**: Use Claude Haiku via OpenRouter for non-critical steps

## Security & Privacy

### MVP Safeguards

1. **Rate limiting**: 5 runs per IP per hour (prevents abuse)
2. **Input sanitization**: Validate optional "direction" field
3. **No PII collection**: Zero user data stored (per Constitution I)
4. **Public sources only**: Respect robots.txt, no private data
5. **API key security**: OpenRouter key in environment variable

### Out of Scope for MVP

- User authentication (blocked by Constitution I)
- GDPR compliance (no PII = not applicable)
- Payment processing (free tier per MVP Constraints)

## Testing Strategy

### Manual Testing (MVP requirement per Constitution)

1. **Happy path**: Start run → Track progress → View results → Export
2. **Error handling**: Kill Redis, verify graceful failure
3. **Rate limiting**: Make 6 requests rapidly, verify 6th blocked
4. **Russian language**: Verify all UI and generated content in Russian

### Automated Testing (post-MVP)

- Contract tests for API endpoints
- Integration tests for LLM pipeline
- Unit tests for critical business logic

## Open Questions (Resolved)

~~1. Should we use a frontend framework?~~
   **RESOLVED**: No, vanilla JS for 1-day speed

~~2. Which job queue library?~~
   **RESOLVED**: RQ (Redis Queue) for simplicity

~~3. Database choice?~~
   **RESOLVED**: SQLite for zero-config MVP

~~4. Deployment platform?~~
   **RESOLVED**: Railway/Render/Fly.io (free tier available)

## Implementation Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenRouter API limits | Medium | High | Use Claude Haiku for non-critical steps, implement backoff |
| Scraping blocked by robots.txt | Medium | Medium | Maintain list of allowed sources, respect rate limits |
| 10-min Bronze target missed | High | Medium | Focus on parallel execution, accept Bronze as acceptable |
| Redis setup complexity | Low | Medium | Use Railway Redis add-on (zero config) |
| Russian language quality issues | Medium | Medium | Use native Russian prompts, validate with real users |

## Timeline Estimate (1-Day Breakdown)

| Phase | Duration | Tasks |
|-------|----------|-------|
| Setup | 1 hour | Project structure, FastAPI scaffold, SQLite models |
| Worker pipeline | 3 hours | RQ workers, scraping, LLM integration |
| API routes | 2 hours | Run CRUD, progress SSE, export |
| Frontend | 2 hours | 4 HTML pages, basic styling, JS logic |
| Testing & Polish | 2 hours | Manual testing, error handling, deployment |

**Total**: ~10 hours (feasible in 1 intense workday)

## Success Criteria Validation

✅ All research questions resolved
✅ Technology choices support Constitution principles
✅ 1-day timeline feasible with chosen stack
✅ No blocking dependencies identified
✅ Security baseline defined
