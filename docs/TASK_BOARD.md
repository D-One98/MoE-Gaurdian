# MoE-GUARDIAN — Team Task Board

## Divy Mishra (Backend, AI Orchestration, Security & DevOps)
- [x] Session 1: FastAPI foundation, Unified Pydantic Contract, `RuleGuard`, baseline `ClaimGuard`, `VERITY MoE` orchestrator, Maker-Checker HMAC snapshots, and 8 Pytest tests.
- [ ] Session 2: Add SQLite/PostgreSQL persistence, custom rule/fact ingestion endpoints (`POST /api/brand/rules`, `POST /api/brand/facts`), and baseline `VisualGuard` static-image/alt-text check.
- [ ] Session 4: Backend deployment (Render/Railway) and environment variable setup.

## Lavanya Bani (Frontend, UX & Integration Testing)
- [ ] Session 2/3: Initialize frontend app in `frontend/` consuming `shared/contracts.ts`.
- [ ] Session 3: Build Demo Role Switcher (`CREATOR`, `BRAND_MANAGER`, `AUTHORISED_REVIEWER`, `WORKSPACE_ADMIN`), 1-click Sample Draft loader (`GET /api/demo/workspace`), block editor with inline finding cards, "Apply Verified Rewrite" action, and Maker-Checker review/snapshot panel.

## Shared Integration Tasks
- [ ] Verify end-to-end flow between frontend editor blocks (`document_block_id`) and `POST /api/audits` + `POST /api/audits/{audit_id}/review`.