## Divy Mishra (Backend, AI Orchestration, Security & DevOps)
- [x] Session 1: FastAPI foundation, Unified Pydantic Contract, `RuleGuard`, baseline `ClaimGuard`, `VERITY MoE` orchestrator, Maker-Checker HMAC snapshots, and 8 Pytest tests.
- [x] Session 2 (Phase 1): SQLAlchemy 2.x ORM models, SQLite/PostgreSQL database session management, `GovernanceRepository`, and idempotent seeding.
- [x] Session 2 (Phase 2): `POST /api/brand/rules` and `POST /api/brand/facts` ingestion APIs with `409 Conflict` duplicate handling.
- [x] Session 2 (Phase 3): Deterministic `VisualGuard` baseline (PNG/JPEG validation, CIEDE2000 $\Delta E$ palette check, WCAG contrast / `INSUFFICIENT_DATA`, `alt_text` check).
- [x] Session 2 (Phases 4–6): Fail-closed multi-engine orchestration, signed `review_notes` HMAC verification, 27-test regression suite, and documentation sync.
- [ ] Session 4: Backend deployment (Render/Railway) and environment variable setup.

## Lavanya Bani (Frontend, UX & Integration Testing)
- [ ] Session 3: Build frontend workspace in `frontend/` consuming `shared/contracts.ts`.
- [ ] Session 3: Implement Demo Role Switcher, Sample Draft loader, custom Rule/Fact creation modals, block editor with inline finding cards, optional static-image upload for `VisualGuard`, and Maker-Checker review/snapshot panel.

## Shared Integration Tasks
- [ ] Verify end-to-end flow between frontend editor/upload components and the persistent Session 2 backend endpoints.