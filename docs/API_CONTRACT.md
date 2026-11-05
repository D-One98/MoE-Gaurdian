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