# Implementation Plan: Pain-to-Idea Generator MVP

**Branch**: `001-pain-to-idea-mvp` | **Date**: 2026-02-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-pain-to-idea-mvp/spec.md`

## Summary

Build a 1-day MVP web application that generates 10-20 business ideas from real user pains found in public discussions. System must work асинхронно without user registration, display progress in real-time, and provide complete idea packages with evidence, competitors, and implementation plans in Russian.

**Core value**: Transforms weeks of manual customer discovery into minutes of automated analysis with transparent evidence.

## Technical Context

**Language/Version**: Python 3.14 (confirmed installed on Windows 10)
**Primary Dependencies**: FastAPI, RQ (Redis Queue), SQLite, httpx, Playwright, BeautifulSoup4
**Storage**: SQLite (file-based database, 24-hour retention minimum)
**Testing**: Manual testing for MVP (automated tests post-MVP)
**Target Platform**: Web application (backend: Python/FastAPI, frontend: vanilla HTML/CSS/JS)
**Project Type**: Web application (backend + frontend separation)
**Performance Goals**:
- UI response <1s (p95)
- Generation complete in ≤10 min (Bronze), target 3 min (Silver), stretch 60s (Gold)
- Support 50 concurrent users without degradation
**Constraints**:
- OpenRouter API only for LLM (per Constitution)
- No authentication/registration (per Constitution)
- Russian language only for all UI and content (per Constitution)
- 24-hour data retention minimum (per NFR)
- 1-day implementation timeline (per Constitution)
**Scale/Scope**: MVP handling 10-50 DAU, 10-20 concurrent users, ~1000 runs total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: 1-Day MVP First ✅

- [x] NO user registration or authentication
- [x] NO personal data collection
- [x] Core flow only: start run → track progress → view ideas → export
- [x] Simplest implementation (SQLite, vanilla JS, minimal dependencies)
- [x] Technical debt acceptable for speed

**Status**: PASS - All requirements met

### Principle II: Russian Language Invariant ✅

- [x] All UI text in Russian (buttons, labels, messages)
- [x] All generated content in Russian (pains, ideas, plans, evidence)
- [x] Error messages in Russian
- [x] Export format in Russian
- [x] Exception: Brand names can remain in original language

**Status**: PASS - Language requirements enforced in spec and data model

### Principle III: Asynchronous Generation ✅

- [x] Run returns ID immediately
- [x] Execution in background (RQ workers + Redis)
- [x] UI shows progress (SSE implementation)
- [x] Results available when ready
- [x] Performance targets: ≤10 min (Bronze), ≤3 min (Silver), ≤60s (Gold)

**Status**: PASS - Async architecture with RQ + SSE progress

### Principle IV: Evidence Transparency ✅

- [x] Structured signals for each pain
- [x] Confidence level (high/medium/low) explicit
- [x] "Why this is money pain" explanation
- [x] Sources/links in "Details" expansion
- [x] Brief view (2-5 lines) + detailed view pattern

**Status**: PASS - Evidence model supports transparency requirements

### Principle V: Idea Pack Completeness ✅

- [x] Pain description (1 paragraph)
- [x] Who suffers (segment)
- [x] Evidence signals
- [x] Minimum 2-3 analogues with links
- [x] Implementation plans (7-day and 30-day)
- [x] Confidence score (high/medium/low)
- [x] Output: 10-20 ideas per run

**Status**: PASS - Data model enforces all 6 components

### MVP Constraints Compliance ✅

- [x] OpenRouter only for LLM
- [x] Local/free services (SQLite, Redis)
- [x] No auth/accounts
- [x] No billing
- [x] Basic export only (Markdown)
- [x] Public sources only
- [x] 24-hour retention acceptable

**Status**: PASS - All constraints respected

**Gate Result**: ✅ PASS - No violations, ready for Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-pain-to-idea-mvp/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Database schema
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Phase 2: Implementation tasks (/speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure (backend + frontend)

backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings and configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── run.py
│   │   ├── idea.py
│   │   ├── analogue.py
│   │   ├── evidence.py
│   │   └── init_db.py         # Database initialization
│   ├── api/                    # FastAPI routes
│   │   ├── __init__.py
│   │   ├── runs.py            # Run CRUD + progress SSE
│   │   ├── ideas.py           # Ideas retrieval
│   │   └── export.py          # Markdown export
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── run_service.py     # Run orchestration
│   │   ├── idea_service.py    # Idea retrieval
│   │   └── export_service.py  # Export generation
│   ├── workers/                # RQ background workers
│   │   ├── __init__.py
│   │   ├── run_worker.py      # Main worker entry
│   │   └── generation_pipeline.py  # Generation stages
│   ├── llm/                    # OpenRouter integration
│   │   ├── __init__.py
│   │   ├── client.py          # API client
│   │   └── prompts.py         # Russian prompts
│   └── scrapers/               # Public source scrapers
│       ├── __init__.py
│       ├── base.py            # Base scraper class
│       ├── reddit.py          # Reddit scraper
│       └── forums.py          # Forum scrapers
├── tests/
│   ├── test_api.py
│   └── test_models.py
├── logs/
├── requirements.txt
├── .env.example
└── README.md

frontend/
├── index.html               # Landing + start run (User Story 1)
├── status.html              # Progress tracking (User Story 2)
├── results.html             # Ideas list (User Story 3)
├── detail.html              # Idea details (User Story 4)
├── assets/
│   ├── app.js               # Vanilla JS for all pages
│   ├── api.js               # API client wrapper
│   └── styles.css           # Custom styles (optional)
└── README.md

.specify/
├── memory/
│   └── constitution.md      # Project constitution
├── templates/               # Spec templates
└── scripts/                 # Automation scripts

lean_canvas/                 # Product documentation
├── 01-brief.md
├── 02-user-story-map.md
├── 04-nfr.md
├── 05-lean-canvas.md
├── 07-c4-architecture.md
└── adr/                     # Architecture Decision Records
```

**Structure Decision**: Web application with clear backend/frontend separation. Backend handles all business logic and async workers. Frontend is minimal vanilla JS for 1-day speed. No build tooling required.

## Complexity Tracking

> **No violations to justify** - All Constitution principles followed without exceptions.

## Phase 0: Research & Technology Decisions

**Status**: ✅ COMPLETED
**Output**: [research.md](research.md)

### Research Findings Summary

1. **Stack**: Python 3.14 + FastAPI + vanilla JS (no frontend framework)
2. **Job Queue**: RQ (Redis Queue) - simplest Python-native solution
3. **Database**: SQLite - zero config, sufficient for MVP scale
4. **LLM**: Direct OpenRouter API via httpx
5. **Scraping**: Playwright + BeautifulSoup4 hybrid
6. **Progress**: Server-Sent Events (SSE) via FastAPI
7. **Deployment**: Railway/Render/Fly.io free tier
8. **Rate Limiting**: slowapi library (IP-based)
9. **Export**: Python-Markdown with templates

**Key Decision**: Prioritize simplicity over scalability for 1-day MVP. All choices optimize for minimal setup and rapid iteration.

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETED
**Prerequisites**: research.md complete

### Outputs

1. ✅ **data-model.md**: SQLite schema with 4 entities (Run, Idea, Analogue, Evidence)
2. ✅ **contracts/openapi.yaml**: REST API specification (5 endpoints)
3. ✅ **quickstart.md**: Developer setup and troubleshooting guide

### Data Model Summary

**Entities**:
- **Run**: Tracks generation session (status, progress, error handling)
- **Idea**: Business idea with complete pack (pain, evidence, plans)
- **Analogue**: Competitors/alternatives (minimum 2 per idea)
- **Evidence**: Supporting signals (brief + detailed views)

**Relationships**:
- Run (1) → Idea (N)
- Idea (1) → Analogue (N, min 2)
- Idea (1) → Evidence (N)

**Key Validation**: Idea completeness enforced at application level before marking run as completed.

### API Contracts Summary

**Endpoints**:
1. `POST /api/runs` - Create new generation run
2. `GET /api/runs/{run_id}` - Get run status
3. `GET /api/runs/{run_id}/progress` - SSE progress stream
4. `GET /api/runs/{run_id}/ideas` - List all ideas
5. `GET /api/ideas/{idea_id}` - Get idea details
6. `POST /api/export/markdown` - Export to .md file

**Authentication**: None (per Constitution I)
**Rate Limiting**: 5 runs per IP per hour (slowapi)

### Constitution Check (Post-Design)

Re-evaluated all 5 principles against final design:

✅ **Principle I (1-Day MVP)**: No auth, simple stack, achievable timeline
✅ **Principle II (Russian Language)**: All content fields validated for Russian
✅ **Principle III (Async)**: RQ workers + SSE progress
✅ **Principle IV (Evidence)**: Brief/detailed evidence model
✅ **Principle V (Completeness)**: All 6 components enforced

**Result**: ✅ PASS - Design compliant with all principles

## Phase 2: Task Generation

**Status**: 🔄 NEXT PHASE
**Command**: `/speckit.tasks`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Output**: `tasks.md` with dependency-ordered implementation tasks

**Expected Task Structure**:
1. **Phase 1: Setup** - Project structure, dependencies
2. **Phase 2: Foundation** - Database, models, basic API
3. **Phase 3: User Story 1** - Start run functionality
4. **Phase 4: User Story 2** - Progress tracking (SSE)
5. **Phase 5: User Story 3** - View ideas list
6. **Phase 6: User Story 4** - View idea details
7. **Phase 7: User Story 5** - Export to Markdown
8. **Phase 8: Workers** - Generation pipeline (scraping + LLM)
9. **Phase 9: Polish** - Error handling, rate limiting, testing

## Implementation Timeline (1-Day Breakdown)

Based on research.md estimates:

| Time | Phase | Tasks | Owner |
|------|-------|-------|-------|
| 0:00-1:00 | Setup | Project structure, FastAPI scaffold, SQLite models | Dev |
| 1:00-4:00 | Workers | RQ workers, scraping, LLM integration | Dev |
| 4:00-6:00 | API | Run CRUD, progress SSE, ideas endpoints, export | Dev |
| 6:00-8:00 | Frontend | 4 HTML pages, vanilla JS, basic styling | Dev |
| 8:00-10:00 | Testing | Manual testing, error handling, deployment | Dev |

**Total**: ~10 hours (1 focused workday)

**Critical Path**: Workers (Phase 2) → API (Phase 3) → Frontend (Phase 4)

## Deployment Strategy

### MVP Deployment (Railway recommended)

**Why Railway**:
- Free tier available
- Redis add-on included
- Git push to deploy
- Zero DevOps overhead

**Steps**:
1. Create Railway project
2. Add Redis addon
3. Configure environment variables (OPENROUTER_API_KEY, etc.)
4. Connect GitHub repo (001-pain-to-idea-mvp branch)
5. Deploy automatically on push

**Alternative**: Render, Fly.io (similar workflows)

### Environment Variables (Production)

```env
OPENROUTER_API_KEY=<production-key>
REDIS_URL=<railway-redis-url>
DATABASE_URL=sqlite:///./production.db
ENVIRONMENT=production
LOG_LEVEL=WARNING
RATE_LIMIT_RUNS_PER_HOUR=5
GENERATION_TIMEOUT_SECONDS=600
```

## Testing Strategy

### Manual Testing (MVP Requirement)

**Critical Path Test**:
1. Open frontend → Click "Запустить прогон"
2. Watch progress → Verify Russian stages display
3. Wait for completion (≤10 min)
4. View ideas list → Verify 10-20 ideas
5. Click idea → Verify all 6 components present
6. Export to Markdown → Verify file downloads

**Edge Cases**:
1. OpenRouter API failure → Graceful error message
2. Rate limiting → 6th request blocked
3. Browser closed during generation → Can resume by ID
4. Less than 10 ideas generated → Run marked as failed

### Automated Testing (Post-MVP)

Deferred to post-MVP per Constitution testing strategy.

## Monitoring & Observability

### MVP Metrics (Manual Tracking)

- Runs created per day
- Runs completed successfully (target: 85%+)
- Average generation time (target: <10 min)
- Ideas per run (target: 10-20)
- Ideas with 2+ analogues (target: 95%+)

### Logging

```python
# backend/src/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

**Key Log Points**:
- Run created
- Worker picked up job
- Stage transitions
- LLM API calls (duration, tokens)
- Errors with stack traces

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenRouter API limits | Use Claude Haiku for non-critical steps, implement exponential backoff |
| 10-min Bronze target missed | Accept Bronze as MVP target, optimize in future iterations |
| Redis setup complexity | Use Railway Redis add-on (zero config) |
| Scraping blocked | Maintain whitelist of allowed sources, respect robots.txt |
| Russian language quality | Use native Russian prompts, validate with real users early |

## Success Criteria Validation

Mapping Success Criteria from spec.md to implementation:

- ✅ **SC-001**: Fast start run (<10s) - Single API call, immediate response
- ✅ **SC-002**: 90% runs complete in ≤10min - Worker timeout enforced
- ✅ **SC-003**: 10-20 valid ideas - Application-level validation before completion
- ✅ **SC-004**: 95% ideas have 2+ analogues - Database constraint + validation
- ✅ **SC-005**: 100% Russian language - Language validation in models
- ✅ **SC-006**: 50 concurrent users - SQLite + RQ handles this scale
- ✅ **SC-007**: Export in <5s - Simple file generation
- ✅ **SC-008**: 85% success rate - Error handling + retry logic
- ✅ **SC-009**: 24h retention - Database cleanup job
- ✅ **SC-010**: 80% engagement - Track in post-MVP analytics

## Next Steps

1. ✅ Constitution created
2. ✅ Specification written and validated
3. ✅ Research completed (technology decisions)
4. ✅ Data model defined
5. ✅ API contracts specified
6. ✅ Quickstart guide created
7. 🔄 **NEXT**: Run `/speckit.tasks` to generate implementation tasks
8. ⏳ Run `/speckit.implement` to execute tasks
9. ⏳ Manual testing and deployment
10. ⏳ Gather user feedback from AI Talent Camp

## Notes

- **Python version confirmed**: 3.14 installed, use `python` command (not `python3`)
- **Node.js available**: Can be used for optional tooling if needed
- **Windows 10 environment**: Redis via Docker, WSL, or Memurai recommended
- **OpenRouter key provided**: Ready for integration, monitor usage/costs
- **1-day constraint**: Prioritize working MVP over polish

## References

- **Constitution**: `.specify/memory/constitution.md`
- **Spec**: `specs/001-pain-to-idea-mvp/spec.md`
- **Research**: `specs/001-pain-to-idea-mvp/research.md`
- **Data Model**: `specs/001-pain-to-idea-mvp/data-model.md`
- **API Contracts**: `specs/001-pain-to-idea-mvp/contracts/openapi.yaml`
- **Quickstart**: `specs/001-pain-to-idea-mvp/quickstart.md`
- **Lean Canvas**: `lean_canvas/05-lean-canvas.md`
- **ADRs**: `lean_canvas/adr/ADR-001-async-run.md`, `ADR-002-evidence-transparency.md`, `ADR-003-russian-only.md`
