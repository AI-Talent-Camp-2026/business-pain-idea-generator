<!--
Sync Impact Report:
- Version change: None → 1.0.0 (Initial ratification)
- Modified principles: N/A (Initial creation)
- Added sections: Core Principles (5 principles), MVP Constraints, Development Workflow, Governance
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md (reviewed - Constitution Check section compatible)
  ✅ spec-template.md (reviewed - requirements alignment confirmed)
  ✅ tasks-template.md (reviewed - task categorization reflects principles)
- Follow-up TODOs: None
-->

# Pain-to-Idea Generator Constitution

## Core Principles

### I. 1-Day MVP First (NON-NEGOTIABLE)

The first working version MUST be achievable within 1 day. This means:
- NO user registration, authentication, or account management
- NO personal data collection or storage (PII-free)
- Core flow only: start run → generate ideas → view results → export
- Simplest possible implementation that delivers value
- Technical debt is acceptable if it unblocks the 1-day goal

**Rationale**: Speed to market and early validation are critical. Complex features can be added post-MVP after validating the core value proposition with real users.

### II. Russian Language Invariant (NON-NEGOTIABLE)

All user-facing content MUST be in Russian:
- UI text, labels, buttons, messages
- Pain descriptions, business ideas, plans, evidence
- Error messages and system notifications
- Export formats and documentation

Exceptions:
- Brand names and product names may remain in original language
- Technical logs may be in English
- Multi-language sources are allowed for research, but output MUST be Russian

**Rationale**: Target users are Russian-speaking founders and product managers. Language consistency reduces cognitive load and increases trust (ADR-003).

### III. Asynchronous Generation (NON-NEGOTIABLE)

Idea generation MUST run asynchronously:
- Run starts immediately and returns run ID
- Execution happens in background (job queue + workers)
- UI shows progress status and stages
- Results become available when ready (no page blocking)

Performance targets:
- Bronze: ≤10 minutes
- Silver: ≤3 minutes
- Gold: ≤60 seconds

**Rationale**: Generation can take minutes and has unpredictable duration. Synchronous execution creates poor UX and scalability issues (ADR-001, NFR 1.2).

### IV. Evidence Transparency (NON-NEGOTIABLE)

Every pain/idea MUST include verifiable evidence:
- Structured signals: typical phrases/behavioral patterns people exhibit
- Confidence level: high/medium/low (explicitly marked)
- "Why this is a money pain" explanation
- Sources/links available via "Details" expansion (not cluttering main view)

Default view: brief evidence summary (2-5 lines of patterns)
Details view: links to discussions, anonymized quotes, context

**Rationale**: Trust is the primary product differentiator. Without transparency, this becomes "just another idea generator" (ADR-002, Market Research findings).

### V. Idea Pack Completeness

Every generated idea MUST include:
1. **Pain description**: clear, concrete, 1 paragraph (no vague language)
2. **Who suffers**: segment/persona identification
3. **Evidence signals**: confirmation patterns (see Principle IV)
4. **Analogues**: minimum 2-3 competitors/alternatives with links
5. **Implementation plan**: 7-day and 30-day timeline skeletons
6. **Confidence score**: high/medium/low

Output quantity: 10-20 ideas per run (configurable within range)

**Rationale**: Users need complete information to make decisions, not just inspiration. Incomplete ideas waste user time and reduce conversion (Lean Canvas, User Story Map US-006, US-007).

## MVP Constraints

These constraints apply to the 1-day MVP and may be relaxed post-MVP:

### Technical Budget
- **LLM provider**: OpenRouter only (already paid subscription)
- **Local agents**: Preferred for cost control
- **Other services**: Free tier or local deployment only
- **Infrastructure**: Minimal - optimize for speed to market

### Scope Limitations
- **NO authentication/authorization** (public access or simple access key)
- **NO persistent user accounts or profiles**
- **NO billing/payments** (free mode for camp participants)
- **NO run history persistence** (1-7 days storage acceptable, or session-only)
- **NO favorites, libraries, or advanced filtering** (post-MVP)
- **Basic export only**: Copy markdown or download file (no export history)

### Data Sources
- **Public sources only**: forums, communities, comments, reviews
- **NO private/authenticated sources**: no company data integration on Day-1
- **Mixed RU+EN sources allowed**: but output must be Russian (see Principle II)

## Development Workflow

### Architecture Requirements
- **Async workers**: Separate generation workload from UI/API (see Principle III)
- **Job queue**: Required for async run orchestration
- **Progress tracking**: Users MUST see where generation is in the pipeline
- **Partial results**: System SHOULD handle gracefully (e.g., ideas without analogues)

### Quality Gates
- **Evidence validation**: Before marking run complete, verify all ideas have evidence
- **Analogue validation**: Verify minimum 2 analogues per idea
- **Language validation**: All user-facing text must pass Russian-only check
- **Completeness validation**: All 6 components of Idea Pack present (Principle V)

### Testing Strategy (Optional for MVP)
- Tests are NOT mandatory for 1-day MVP
- If included, focus on:
  - Core flow: start run → get results
  - Evidence structure validation
  - Language invariant checks
  - Async job completion

### Rate Limiting
- **Anti-abuse**: Required even without auth (IP-based or access key)
- **Concurrent runs**: Limit per user/IP to prevent resource exhaustion
- **Target load**: 10-50 concurrent users without UI degradation (NFR 1.1)

## Governance

This constitution defines the **non-negotiable rules** for the Pain-to-Idea Generator project. It supersedes all other practices and guides all design, implementation, and review decisions.

### Amendment Process
1. Proposed changes must be documented with rationale
2. Changes must be reviewed against lean canvas and ADRs
3. Breaking changes require migration plan for existing work
4. Version bump follows semantic versioning (see below)

### Versioning Policy
- **MAJOR**: Backward-incompatible principle changes (e.g., removing "Russian only")
- **MINOR**: New principle added or material expansion of guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review
- All PRs MUST verify compliance with Core Principles (I-V)
- Constitution violations MUST be justified in plan.md "Complexity Tracking" section
- Scope creep beyond MVP Constraints MUST be explicitly approved
- ADRs (Architecture Decision Records) provide detailed rationale for key decisions

### Related Documents
- **lean_canvas/**: Product vision, user stories, NFRs, personas
- **lean_canvas/adr/**: Architecture decision records (ADR-001, ADR-002, ADR-003)
- **specs/**: Feature specifications and implementation plans
- **.specify/templates/**: Template structures for specs, plans, tasks

**Version**: 1.0.0 | **Ratified**: 2026-02-04 | **Last Amended**: 2026-02-04
