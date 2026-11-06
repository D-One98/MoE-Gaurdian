# MoE-GUARDIAN — Bug Log & Known Technical Limitations

| ID | Severity | Component | Description & Reproduction | Status |
| :--- | :--- | :--- | :--- | :--- |
| LIM-001 | LOW | `anchoring.py` | Identical repeated substrings within the same block that share identical 32-character prefix/suffix context return `AMBIGUOUS_FALLBACK_TO_BLOCK` by design so the UI falls back to a block-level warning rather than misplacing an inline highlight. | Documented Design Boundary |
| LIM-002 | LOW | `orchestrator.py` | Resolved in Session 2: In-memory dictionary storage replaced with SQLAlchemy 2.x persistent storage (`audit_records`, `audit_findings`, `review_snapshots`). | **Resolved in Session 2** |
| LIM-003 | LOW | `claim_guard.py` | Baseline `ClaimGuard` uses deterministic keyword, numeric, and required-condition matching; unit conversion (`lakh` vs `million`) and multi-document conflict detection are scoped for Round 3 Improvement 01. | By Design (Round 2 Baseline) |
| LIM-004 | LOW | `visual_guard.py` | Baseline `VisualGuard` does not perform OCR text extraction or AI semantic vision; WCAG contrast is computed only when foreground/background colours are declared or cleanly two-tone ($\ge 90\%$ pixel coverage), returning `INSUFFICIENT_DATA` otherwise. | By Design (Round 2 Baseline) |
| LIM-005 | MEDIUM | `routes.py` | `actor_role` and ingestion endpoints operate within the demo organisation (`ORG-SAMPLE-DEMO-01`) as a role simulation for frictionless judge testing rather than production JWT identity authentication. | Documented Demo Scope |