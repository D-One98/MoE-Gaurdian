# MoE-GUARDIAN — Bug Log & Known Technical Limitations

| ID | Severity | Component | Description & Reproduction | Status |
| :--- | :--- | :--- | :--- | :--- |
| LIM-001 | LOW | `anchoring.py` | Identical repeated substrings within the same block that share identical 32-character prefix/suffix context return `AMBIGUOUS_FALLBACK_TO_BLOCK` by design so the UI falls back to a block-level warning rather than misplacing an inline highlight. | Documented Design Boundary |
| LIM-002 | LOW | `orchestrator.py` | Session 1 stores audit records in an in-memory dictionary (`_audits`) for zero-configuration local execution; restarting the Uvicorn process resets created audits to the clean seed state. | Planned SQLite/Postgres persistence in Session 2 |
| LIM-003 | LOW | `claim_guard.py` | Baseline `ClaimGuard` uses deterministic keyword, numeric, and required-condition matching; unit conversion (`lakh` vs `million`) and multi-document conflict detection are scoped for Improvement 01. | By Design (Round 2 Baseline) |

