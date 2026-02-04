# Tasks: Pain-to-Idea Generator MVP

**Input**: Design documents from `specs/001-pain-to-idea-mvp/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Tests are OPTIONAL for MVP per Constitution. Manual testing checklist included in Phase 9.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/` at repository root
- Paths shown below follow the project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure: backend/src/{api,models,services,workers,llm,scrapers}, backend/tests, backend/logs
- [ ] T002 Create frontend directory structure: frontend/, frontend/assets/
- [ ] T003 [P] Create backend/requirements.txt with dependencies: fastapi, uvicorn, sqlalchemy, python-rq, redis, httpx, playwright, beautifulsoup4, slowapi, python-multipart
- [ ] T004 [P] Create backend/.env.example with required environment variables per quickstart.md
- [ ] T005 [P] Create frontend/assets/app.js with API base URL configuration
- [ ] T006 [P] Create frontend/assets/api.js wrapper for fetch calls to backend API

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create backend/src/config.py with Settings class loading from environment variables
- [ ] T008 Create backend/src/models/__init__.py and define SQLAlchemy base
- [ ] T009 Create backend/src/models/run.py with Run model per data-model.md schema
- [ ] T010 [P] Create backend/src/models/idea.py with Idea model per data-model.md schema
- [ ] T011 [P] Create backend/src/models/analogue.py with Analogue model per data-model.md schema
- [ ] T012 [P] Create backend/src/models/evidence.py with Evidence model per data-model.md schema
- [ ] T013 Create backend/src/models/init_db.py script to initialize SQLite database and create tables
- [ ] T014 Create backend/src/main.py FastAPI app with CORS middleware and health endpoint
- [ ] T015 [P] Create backend/src/llm/client.py OpenRouter API client with httpx and async methods
- [ ] T016 [P] Create backend/src/llm/prompts.py with Russian language prompts for each generation stage
- [ ] T017 Configure slowapi rate limiter in backend/src/main.py (5 runs per IP per hour)
- [ ] T018 Create backend/src/workers/__init__.py and configure RQ connection to Redis

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Start Idea Generation Run (Priority: P1) 🎯 MVP

**Goal**: User can start a generation run with one click, system returns run ID immediately

**Independent Test**: Open frontend index.html, click "Запустить прогон" button, verify system creates run and redirects to status page with run ID in URL

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create backend/src/api/__init__.py and include router registration helper
- [ ] T020 [US1] Create backend/src/api/runs.py with POST /api/runs endpoint per openapi.yaml
- [ ] T021 [US1] Create backend/src/services/run_service.py with create_run() method (creates Run record, enqueues RQ job, returns run_id)
- [ ] T022 [US1] Integrate runs router into backend/src/main.py FastAPI app
- [ ] T023 [P] [US1] Create frontend/index.html with landing page UI in Russian: title, optional direction input field, "Запустить прогон" button
- [ ] T024 [US1] Implement frontend/assets/app.js function startRun() that calls POST /api/runs and redirects to status.html?run_id={id}

**Checkpoint**: At this point, User Story 1 should be fully functional - user can start a run and get redirected to status page

---

## Phase 4: User Story 2 - Track Generation Progress (Priority: P1) 🎯 MVP

**Goal**: User sees real-time progress updates with Russian stage names during async generation

**Independent Test**: After starting run (US1), verify status.html displays current stage in Russian and updates automatically via SSE

### Implementation for User Story 2

- [ ] T025 [P] [US2] Add GET /api/runs/{run_id} endpoint to backend/src/api/runs.py per openapi.yaml
- [ ] T026 [P] [US2] Add GET /api/runs/{run_id}/progress SSE endpoint to backend/src/api/runs.py with StreamingResponse
- [ ] T027 [US2] Implement backend/src/services/run_service.py methods: get_run_status(), stream_progress_events()
- [ ] T028 [P] [US2] Create frontend/status.html with progress UI: current stage display, progress indicator, Russian stage names, auto-redirect on completion
- [ ] T029 [US2] Implement frontend/assets/app.js function trackProgress() using EventSource for SSE connection to /api/runs/{run_id}/progress
- [ ] T030 [US2] Add error handling in frontend/assets/app.js for failed runs (display Russian error message from API)

**Checkpoint**: At this point, User Stories 1 AND 2 work together - user can start run and see progress updates

---

## Phase 5: User Story 3 - View Generated Ideas (Priority: P1) 🎯 MVP

**Goal**: User sees list of 10-20 ideas after generation completes

**Independent Test**: After run completes (US2), verify results.html displays 10-20 idea cards with title, brief pain description, segment, confidence level - all in Russian

### Implementation for User Story 3

- [ ] T031 [P] [US3] Add GET /api/runs/{run_id}/ideas endpoint to backend/src/api/runs.py per openapi.yaml
- [ ] T032 [US3] Create backend/src/api/ideas.py with GET /api/ideas/{idea_id} endpoint stub (full implementation in US4)
- [ ] T033 [US3] Create backend/src/services/idea_service.py with get_ideas_by_run() method
- [ ] T034 [US3] Integrate ideas router into backend/src/main.py FastAPI app
- [ ] T035 [P] [US3] Create frontend/results.html with ideas list UI: grid of idea cards, each showing title + brief description + segment + confidence badge
- [ ] T036 [US3] Implement frontend/assets/app.js function loadIdeas() that calls GET /api/runs/{run_id}/ideas and renders cards
- [ ] T037 [US3] Add click handler in frontend/assets/app.js to navigate from idea card to detail.html?idea_id={id}

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work - complete flow from start to viewing ideas list

---

## Phase 6: User Story 4 - View Idea Details (Priority: P1) 🎯 MVP

**Goal**: User can click an idea and see complete details: pain, evidence, analogues (2+), plans (7/30 days)

**Independent Test**: Click any idea card from results.html (US3), verify detail.html shows all 6 required components per FR-009

### Implementation for User Story 4

- [ ] T038 [US4] Complete GET /api/ideas/{idea_id} endpoint implementation in backend/src/api/ideas.py per openapi.yaml
- [ ] T039 [US4] Implement backend/src/services/idea_service.py methods: get_idea_full(), get_analogues(), get_evidences()
- [ ] T040 [P] [US4] Create frontend/detail.html with full idea view UI: pain description section, brief evidence (default view), analogues list with links, plan 7 days section, plan 30 days section, confidence badge
- [ ] T041 [US4] Implement frontend/assets/app.js function loadIdeaDetail() that calls GET /api/ideas/{idea_id} and renders all sections
- [ ] T042 [US4] Add "Подробнее" button toggle in frontend/assets/app.js to show/hide detailed evidence (sources, quotes)
- [ ] T043 [US4] Validate all text displayed is in Russian (titles, labels, content) per FR-002 and FR-010

**Checkpoint**: At this point, User Stories 1-4 complete - full core flow works end-to-end

---

## Phase 7: User Story 5 - Export Ideas to Markdown (Priority: P2)

**Goal**: User can export all ideas or selected ideas to downloadable .md file

**Independent Test**: On results.html, click "Экспортировать все" button, verify .md file downloads with correct structure for all ideas in Russian

### Implementation for User Story 5

- [ ] T044 [P] [US5] Create backend/src/api/export.py with POST /api/export/markdown endpoint per openapi.yaml
- [ ] T045 [US5] Create backend/src/services/export_service.py with generate_markdown() method using template
- [ ] T046 [US5] Integrate export router into backend/src/main.py FastAPI app
- [ ] T047 [P] [US5] Add checkboxes to idea cards in frontend/results.html for selection
- [ ] T048 [P] [US5] Add "Экспортировать все" and "Экспортировать выбранное" buttons to frontend/results.html
- [ ] T049 [US5] Implement frontend/assets/app.js function exportIdeas() that calls POST /api/export/markdown with run_id and optional idea_ids, triggers file download
- [ ] T050 [US5] Create Markdown template in backend/src/services/export_service.py with Russian headers and proper formatting for all 6 idea components

**Checkpoint**: All user stories (1-5) now complete and independently functional

---

## Phase 8: Background Workers - Generation Pipeline (Foundational for Generation)

**Purpose**: Implement async workers that perform actual idea generation

**Note**: This phase can be developed in parallel with frontend phases 3-7, but must be complete for end-to-end testing

- [ ] T051 Create backend/src/scrapers/base.py with BaseScraper abstract class
- [ ] T052 [P] Create backend/src/scrapers/reddit.py with RedditScraper implementation using Playwright
- [ ] T053 [P] Create backend/src/scrapers/forums.py with ForumScraper implementation using BeautifulSoup4
- [ ] T054 Create backend/src/workers/generation_pipeline.py with main generation orchestrator function
- [ ] T055 Implement Stage 1 "Поиск сигналов" in backend/src/workers/generation_pipeline.py: scrape public sources, extract pain signals
- [ ] T056 Implement Stage 2 "Анализ болей" in backend/src/workers/generation_pipeline.py: call OpenRouter LLM to cluster pains using prompts from llm/prompts.py
- [ ] T057 Implement Stage 3 "Генерация идей" in backend/src/workers/generation_pipeline.py: call OpenRouter LLM to generate 10-20 ideas with pain descriptions and segments
- [ ] T058 Implement Stage 4 "Поиск аналогов" in backend/src/workers/generation_pipeline.py: search for 2-3 competitors per idea, create Analogue records
- [ ] T059 Implement Stage 5 "Создание планов" in backend/src/workers/generation_pipeline.py: call OpenRouter LLM to generate 7-day and 30-day plans in Russian
- [ ] T060 Implement backend/src/workers/generation_pipeline.py validation: ensure each idea has 2+ analogues, all required fields, Russian language
- [ ] T061 Create backend/src/workers/run_worker.py with RQ worker that executes generation_pipeline and updates Run status/progress
- [ ] T062 Add progress update hooks in backend/src/workers/generation_pipeline.py to update Run.current_stage after each stage
- [ ] T063 Add error handling in backend/src/workers/generation_pipeline.py: catch OpenRouter API errors, mark Run as failed with Russian error message per FR-018
- [ ] T064 Implement timeout enforcement in backend/src/workers/generation_pipeline.py: abort if generation exceeds 600 seconds (Bronze target) per FR-008

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T065 [P] Add Russian error messages for all API error responses in backend/src/api/ routes
- [ ] T066 [P] Add logging configuration in backend/src/config.py with file handler to backend/logs/app.log
- [ ] T067 [P] Add logging statements in backend/src/workers/generation_pipeline.py for each stage start/completion/error
- [ ] T068 Create backend/src/models/cleanup.py script to delete runs older than 24 hours per FR-015
- [ ] T069 [P] Add frontend loading spinners and transitions in frontend/assets/app.js for better UX
- [ ] T070 [P] Add basic CSS styling to frontend pages using TailwindCSS CDN (or minimal custom CSS)
- [ ] T071 Validate all frontend text is in Russian in index.html, status.html, results.html, detail.html per FR-002
- [ ] T072 Add meta tags and favicon to all frontend HTML pages
- [ ] T073 Test rate limiting: make 6 consecutive run requests, verify 6th returns 429 error per FR-016
- [ ] T074 Run manual testing checklist from quickstart.md: verify all user stories work end-to-end
- [ ] T075 Create backend/README.md with setup instructions, API documentation link, and environment variables
- [ ] T076 Create frontend/README.md with development server instructions and file structure
- [ ] T077 Update root README.md with project overview, quickstart link, and deployment instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational
  - US2 (Phase 4): Depends on US1 completion (needs run creation)
  - US3 (Phase 5): Depends on US2 completion (needs run completion)
  - US4 (Phase 6): Depends on US3 completion (needs ideas list)
  - US5 (Phase 7): Depends on US3 completion (can work in parallel with US4)
- **Workers (Phase 8)**: Depends on Foundational phase - can work in parallel with US3-7 frontend work
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs run ID from creation) - Should complete before US3
- **User Story 3 (P1)**: Depends on US2 (needs completed run) - Can partially parallel with US4/US5 frontend work
- **User Story 4 (P1)**: Depends on US3 (needs idea list) - Independent from US5
- **User Story 5 (P2)**: Depends on US3 (needs ideas) - Can work in parallel with US4

### Within Each User Story

- Frontend tasks marked [P] can often run in parallel with backend [P] tasks (different files)
- API routes before service layer before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1 (Setup): All tasks can run in parallel (T003-T006 are independent file creations)
- Phase 2 (Foundational): Models (T010-T012) can run in parallel, LLM client and prompts (T015-T016) can run in parallel
- Within US1: Backend API (T019-T022) and Frontend (T023-T024) can partially overlap
- Within US2: GET endpoint (T025) and SSE endpoint (T026) can run in parallel, Frontend HTML (T028) and JS (T029) can overlap
- Within US3: API work (T031-T034) can run while Frontend (T035-T037) is being built
- Within US4: Backend service methods (T038-T039) and Frontend UI (T040-T042) can overlap
- Within US5: Backend export (T044-T046) and Frontend UI (T047-T049) can work in parallel
- Phase 8 (Workers): Scrapers (T052-T053) can run in parallel, generation stages (T055-T059) are sequential
- Phase 9 (Polish): Most tasks are independent and can run in parallel (T065-T072)

---

## Parallel Example: User Story 1

```bash
# Launch backend and frontend work together:
Task T019-T022: Backend API implementation (1 developer)
Task T023-T024: Frontend HTML + JS (1 developer or same developer after backend)

# All can be developed simultaneously if team has 2+ developers
```

---

## Implementation Strategy

### MVP First (User Stories 1-4 Only - Core Flow)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T018) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T019-T024) - Start run
4. Complete Phase 4: User Story 2 (T025-T030) - Track progress
5. Complete Phase 5: User Story 3 (T031-T037) - View ideas list
6. Complete Phase 6: User Story 4 (T038-T043) - View idea details
7. Complete Phase 8: Background Workers (T051-T064) - CRITICAL for generation
8. **STOP and VALIDATE**: Run manual test checklist, verify all core flows work
9. Deploy MVP (User Stories 1-4 complete)

**MVP Scope**: Phases 1, 2, 3, 4, 5, 6, 8 (Skip US5 export for absolute minimum)

### Full MVP (All User Stories 1-5)

After core MVP validated:
10. Complete Phase 7: User Story 5 (T044-T050) - Export functionality
11. Complete Phase 9: Polish (T065-T077) - Error handling, logging, cleanup, documentation
12. Deploy full MVP

### Incremental Delivery

1. Foundation → Core Flow (US1-4) → Test → Deploy (Day 1 Target)
2. Add Export (US5) → Test → Deploy (Day 2 Enhancement)
3. Polish & Monitoring → Deploy (Day 3 Improvement)

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 2 developers:

1. Both complete Setup + Foundational together
2. Once Foundational done:
   - **Developer A**: User Stories 1-4 (frontend focus)
   - **Developer B**: Phase 8 Workers (backend generation pipeline)
3. Integrate and test together
4. Developer A continues with US5 + Polish while Developer B handles deployment

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify all Russian language requirements during US4 implementation (T043)
- Workers (Phase 8) are critical but can develop in parallel with frontend UI work
- Rate limiting test (T073) requires 6 sequential requests
- Commit after each phase or logical task group
- Stop at any checkpoint to validate story independently
- Total tasks: 77 (manageable for 1-2 day implementation with focused effort)

---

## Manual Testing Checklist (Phase 9 - T074)

Execute these tests to validate MVP:

### Core Flow Test
- [ ] Open http://localhost:3000 (or deployment URL)
- [ ] Click "Запустить прогон" button
- [ ] Verify redirect to status page with run ID in URL
- [ ] Watch progress indicators, verify stages display in Russian
- [ ] Wait for completion (should be ≤10 minutes)
- [ ] Verify auto-redirect to results page

### Ideas List Test (US3)
- [ ] Verify 10-20 idea cards displayed
- [ ] Verify each card shows: title, brief pain, segment, confidence level
- [ ] Verify all text is in Russian (no English except brand names)

### Idea Details Test (US4)
- [ ] Click on an idea card
- [ ] Verify detail page shows all 6 components:
  - [ ] Pain description (1 paragraph)
  - [ ] Segment (who suffers)
  - [ ] Brief evidence (2-5 lines)
  - [ ] Minimum 2 analogues with working links
  - [ ] Plan for 7 days
  - [ ] Plan for 30 days
  - [ ] Confidence level badge
- [ ] Click "Подробнее" button in evidence section
- [ ] Verify detailed evidence expands (sources, quotes)

### Export Test (US5)
- [ ] Return to results page
- [ ] Click "Экспортировать все"
- [ ] Verify .md file downloads
- [ ] Open file, verify contains all ideas in readable Markdown format with Russian text
- [ ] Return to results page, select 2 ideas with checkboxes
- [ ] Click "Экспортировать выбранное"
- [ ] Verify .md file contains only 2 selected ideas

### Error Handling Test
- [ ] Stop Redis server (simulate worker failure)
- [ ] Start new run
- [ ] Verify graceful error message displayed in Russian after timeout
- [ ] Restart Redis

### Rate Limiting Test
- [ ] Make 5 run requests rapidly (within 1 hour)
- [ ] All 5 should succeed
- [ ] Make 6th request
- [ ] Verify 429 error response with Russian message

### Persistence Test
- [ ] Create a run, note the run_id
- [ ] Close browser completely
- [ ] Wait 5 minutes
- [ ] Open browser, navigate directly to results page with run_id
- [ ] Verify ideas still load correctly (24-hour retention per FR-015)

### Pass Criteria
- [ ] All core flow tests pass
- [ ] All ideas have 2+ analogues
- [ ] All text is in Russian
- [ ] Export generates valid Markdown
- [ ] Rate limiting blocks 6th request
- [ ] Runs complete in ≤10 minutes (Bronze target)
