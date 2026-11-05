# MoE-GUARDIAN — System Architecture (Round 2 Foundation)

## 1. System Boundaries & Core Principles
* **Product Identity:** MoE-GUARDIAN (Powered by VERITY MoE)
* **Team:** THE MOE (Divy Mishra & Lavanya Bani)
* **Role:** Pre-publication brand-governance and compliance layer positioned between content creation and publication.
* **Deterministic First:** Explicit rules (`RuleGuard`) and baseline fact/condition comparisons (`ClaimGuard`) execute in pure Python without LLM latency or hallucination.
* **Backend Authority:** Only backend database/seed records serve as authoritative citations (`EvidenceReference`). Rewrite validation statuses (`revalidation_passed`) and HMAC-SHA256 audit snapshots are computed exclusively on the backend.

## 2. End-to-End Data Flow
1. **Workspace & Constitution Loading:** `VerityMoEOrchestrator` loads active `BrandRule` and `ApprovedFact` records.
2. **Mandatory-Policy Enforcement:** Rules marked `mandatory_flag = True` are locked in first so routing/classification never skips required checks.
3. **Specialist Engine Execution:**
   * `RuleGuard` (`backend/app/engines/rule_guard.py`): Evaluates banned terms, exact brand casing (`AURORAGEAR`), mandatory disclaimers, and explicit numeric bounds.
   * `ClaimGuard` Baseline (`backend/app/engines/claim_guard.py`): Evaluates factual/promotional assertions against the Approved Facts Vault across `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, and `UNVERIFIABLE` states.
4. **Canonical Block Anchoring (`backend/app/services/anchoring.py`):** Resolves `matched_text`, `prefix_context`, and `suffix_context` within each submitted `document_block_id` without inventing frontend character offsets.
5. **Fail-Closed Rewrite Validation Coordinator:** Candidate rewrites are re-checked through `RuleGuard` and `ClaimGuard`; `revalidation_passed = True` is assigned by the backend only when `RuleGuard` reports 0 violations and `candidate_verification_status == "SUPPORTED"`.
6. **Maker-Checker & HMAC Audit Snapshot:** Creators are blocked from self-approving (`403 Forbidden`). Validated approvals generate a canonicalised, `HMAC-SHA256` signed `AuditSnapshotRecord` chained to `previous_snapshot_hmac`.

## 3. LLM Boundary & Security Limitations
* **LLM Boundary (`backend/app/services/llm_adapter.py`):** Isolated behind `LLMProviderAdapter` (defaults to `NullDeterministicAdapter`). Local execution requires zero external API keys, and a failed/unconfigured LLM never produces a `SUPPORTED` claim.
* **Current Security Scope:** Public demo endpoints use non-sensitive fictional sample data (`AURORAGEAR`). Role selection in the demo workspace is a simulation for frictionless judge testing; server-side state validation enforces Maker-Checker separation.