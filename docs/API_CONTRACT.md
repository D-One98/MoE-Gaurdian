# MoE-GUARDIAN — Frontend/Backend API Contract

* **Backend Source of Truth:** `backend/app/schemas/contracts.py`
* **Shared TypeScript Contract:** `shared/contracts.ts`
* **Base URL (Local):** `http://localhost:8000`
* **Interactive Swagger UI:** `http://localhost:8000/docs`

---

## 1. Allowed Orthogonal Enum Values

* **`ExecutionState`:** `"OK"` | `"NOT_APPLICABLE"` | `"INSUFFICIENT_DATA"` | `"ERROR"`
* **`FindingType`:** `"DETERMINISTIC_VIOLATION"` | `"FACTUAL_CLAIM"` | `"TONE_MESSAGING"` | `"VISUAL_A11Y_SUBSET"`
* **`VerificationStatus`:** `"SUPPORTED"` | `"PARTIAL"` | `"CONTRADICTED"` | `"UNVERIFIABLE"` | `"NOT_CLAIM_APPLICABLE"`
* **`Severity`:** `"CRITICAL"` | `"HIGH"` | `"MEDIUM"` | `"LOW"` | `"INFO"`
* **`AnchorResolutionStatus`:** `"RESOLVED_UNIQUE"` | `"AMBIGUOUS_FALLBACK_TO_BLOCK"` | `"UNRESOLVED_SIDEBAR_ONLY"`
* **`DemoRole`:** `"CREATOR"` | `"BRAND_MANAGER"` | `"AUTHORISED_REVIEWER"` | `"WORKSPACE_ADMIN"`
* **`AuditStatus`:** `"PENDING_REVIEW"` | `"READY_FOR_MANAGER_APPROVAL"` | `"ESCALATED_TO_AUTHORISED_REVIEWER"` | `"APPROVED"` | `"CHANGES_REQUESTED"`

---

## 2. Endpoints

### `GET /api/health`
Returns service health and version metadata.

### `GET /api/demo/workspace`
Returns the pre-seeded fictional demo brand (`AURORAGEAR`), allowed `DemoRole` list, and 3 ready-to-load `sample_drafts` for 1-click judge testing.

### `GET /api/brand/rules` & `GET /api/brand/facts`
Returns active Brand Constitution rules and Approved Facts Vault entries.

### `POST /api/audits`
Runs a full `VERITY MoE` governance audit on canonical content blocks.
* **Request Body (`AuditCreateRequest`):**
```json
{
  "campaign_id": "CAMP-DEMO-2026",
  "submitted_by_role": "CREATOR",
  "blocks": [
    {
      "document_block_id": "blk-p1",
      "text": "AURORAGEAR delivers 12 hours of guaranteed battery life on a single charge!"
    }
  ],
  "alt_text": null
}

Response (201 Created — AuditResponse): Returns audit_id, document_revision_hash, overall_status, engine_executions, findings (each with backend-resolved evidence_reference and optional fail-closed rewrite_candidate), and ai_disclosure_log.

GET /api/audits/{audit_id}
Retrieves an existing AuditResponse by ID. Returns 404 with {"detail": {"error": "AUDIT_NOT_FOUND", "message": "..."}} if not found.

POST /api/audits/{audit_id}/review
Records a human review decision and generates an HMAC-SHA256 signed AuditSnapshotRecord.

Request Body (ReviewDecisionRequest):

JSON
{
  "actor_role": "AUTHORISED_REVIEWER",
  "decision": "APPROVE",
  "override_justification": "Approved for internal teaser with lab testing footnote."
}
Validation Rules:

Returns 403 Forbidden if actor_role == "CREATOR" (Maker-Checker enforcement).

Returns 403 Forbidden if overall_status == "ESCALATED_TO_AUTHORISED_REVIEWER" and actor_role is not "AUTHORISED_REVIEWER" or "WORKSPACE_ADMIN".

Returns 400 Bad Request if approving a draft with non-SUPPORTED findings without a non-empty override_justification.

# MoE-GUARDIAN — Project State (Session 2 Complete)

## 1. Implemented & Verified in Sessions 1 & 2
* **FastAPI & Unified Contracts:** Strict orthogonal Pydantic v2 schemas (`backend/app/schemas/contracts.py`) and synchronized TypeScript interfaces (`shared/contracts.ts`).
* **SQLAlchemy 2.x Persistence (`backend/app/core/database.py`, `backend/app/models/orm_models.py`, `backend/app/repositories/governance_repo.py`):** Persistent storage for `BrandRuleModel`, `ApprovedFactModel`, `AuditRecordModel`, `AuditFindingModel`, and `ReviewSnapshotModel` with SQLite foreign-key enforcement, idempotent demo seeding, and transaction rollback.
* **Brand Ingestion APIs (`POST /api/brand/rules`, `POST /api/brand/facts`):** Validated custom rule and fact ingestion with `409 Conflict` duplicate protection and immediate availability in subsequent audits.
* **Deterministic Specialist Engines:**
  * `RuleGuard`: Banned terms, brand casing (`AURORAGEAR`), mandatory disclaimers, and discount bounds.
  * `ClaimGuard` Baseline: 4-state claim verification (`SUPPORTED`, `PARTIAL`, `CONTRADICTED`, `UNVERIFIABLE`) and fail-closed Rewrite Validation Coordinator.
  * `VisualGuard` Baseline: Static PNG/JPEG validation, 5 MB size cap, 16 MP decompression-bomb protection, CIEDE2000 ($\Delta E$) brand palette comparison, `alt_text` check, and WCAG relative-luminance contrast (with `INSUFFICIENT_DATA` escalation when foreground/background regions cannot be reliably isolated).
* **Hardened HMAC-SHA256 Review Snapshots:** Canonical snapshot signing covering `review_notes`, chained via `previous_snapshot_hmac` in persistent storage, with cryptographic tamper verification (`VerityMoEOrchestrator.verify_snapshot_hmac`).
* **Automated Test Suite:** **27 passing Pytest tests** across 4 test modules using isolated temporary SQLite databases (`backend/tests/conftest.py`).

## 2. Remaining Work for Subsequent Sessions
* **Session 3 (Frontend & End-to-End User Workflow):** Connect `frontend/` UI to the Session 2 backend endpoints (`GET /api/demo/workspace`, `GET/POST /api/brand/rules`, `GET/POST /api/brand/facts`, `POST /api/audits`, `POST /api/audits/{audit_id}/review`).
* **Session 4 (Deployment & Hardening):** Public cloud deployment (Vercel + Render/Railway) and Round 2 submission package verification.