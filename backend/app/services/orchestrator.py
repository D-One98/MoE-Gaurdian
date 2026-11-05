import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.core.config import settings
from app.schemas.contracts import (
    AuditCreateRequest,
    AuditResponse,
    AuditStatus,
    AuditSnapshotRecord,
    ContentBlock,
    DemoRole,
    ExecutionState,
    Severity,
    UnifiedFinding,
    VerificationStatus,
)
from app.services.seed_data import (
    DEMO_ORG_ID,
    get_demo_approved_facts,
    get_demo_brand_rules,
)
from app.engines.rule_guard import run_rule_guard
from app.engines.claim_guard import run_claim_guard_baseline


class VerityMoEOrchestrator:
    def __init__(self) -> None:
        self._audits: Dict[str, AuditResponse] = {}
        self._last_snapshot_hmac: str = "GENESIS_SNAPSHOT_0000000000000000"

    @staticmethod
    def compute_document_revision_hash(blocks: List[ContentBlock], alt_text: Optional[str] = None) -> str:
        canonical = {
            "blocks": [{"document_block_id": b.document_block_id, "text": b.text.strip()} for b in blocks],
            "alt_text": (alt_text or "").strip(),
        }
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"sha256:{hashlib.sha256(payload).hexdigest()}"

    def run_audit(self, request: AuditCreateRequest) -> AuditResponse:
        rules = get_demo_brand_rules()
        facts = get_demo_approved_facts()

        mandatory_rules = [r for r in rules if r.mandatory_flag]
        active_rules = mandatory_rules + [r for r in rules if not r.mandatory_flag]

        rg_findings, rg_exec = run_rule_guard(request.blocks, active_rules)
        cg_findings, cg_exec = run_claim_guard_baseline(request.blocks, facts, active_rules)

        all_findings: List[UnifiedFinding] = rg_findings + cg_findings
        engine_executions = [rg_exec, cg_exec]

        any_engine_failed = any(
            e.execution_state in (ExecutionState.ERROR, ExecutionState.INSUFFICIENT_DATA)
            for e in engine_executions
        )
        has_high_risk_finding = any(
            f.severity in (Severity.CRITICAL, Severity.HIGH)
            or f.verification_status in (
                VerificationStatus.PARTIAL,
                VerificationStatus.CONTRADICTED,
                VerificationStatus.UNVERIFIABLE,
            )
            for f in all_findings
        )

        if any_engine_failed or has_high_risk_finding:
            overall_status = AuditStatus.ESCALATED_TO_AUTHORISED_REVIEWER
            human_review_required = True
        else:
            overall_status = AuditStatus.READY_FOR_MANAGER_APPROVAL
            human_review_required = True

        doc_rev_hash = self.compute_document_revision_hash(request.blocks, request.alt_text)
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        now_utc = datetime.now(timezone.utc).isoformat()

        response = AuditResponse(
            audit_id=audit_id,
            org_id=DEMO_ORG_ID,
            campaign_id=request.campaign_id,
            submitted_by_role=request.submitted_by_role,
            document_revision_hash=doc_rev_hash,
            overall_status=overall_status,
            human_review_required=human_review_required,
            mandatory_policies_enforced=True,
            engine_executions=engine_executions,
            findings=all_findings,
            blocks=request.blocks,
            ai_disclosure_log={
                "llm_provider": settings.llm_provider,
                "external_data_shared": False,
                "deterministic_engines_executed": ["RuleGuard", "ClaimGuard_Baseline"],
                "privacy_masking_mode": "BASELINE_REGEX_ACTIVE",
                "timestamp_utc": now_utc,
            },
            latest_snapshot=None,
            created_at_utc=now_utc,
        )

        self._audits[audit_id] = response
        return response

    def get_audit(self, audit_id: str) -> Optional[AuditResponse]:
        return self._audits.get(audit_id)

    def record_review_decision(
        self,
        audit_id: str,
        actor_role: DemoRole,
        decision: str,
        override_justification: Optional[str] = None,
    ) -> AuditResponse:
        audit = self._audits.get(audit_id)
        if not audit:
            raise KeyError(f"Audit '{audit_id}' not found.")

        if actor_role == DemoRole.CREATOR:
            raise PermissionError("Maker-Checker violation: Content Creators cannot approve or sign off their own submissions.")

        if (
            decision == "APPROVE"
            and audit.overall_status == AuditStatus.ESCALATED_TO_AUTHORISED_REVIEWER
            and actor_role not in (DemoRole.AUTHORISED_REVIEWER, DemoRole.WORKSPACE_ADMIN)
        ):
            raise PermissionError(
                "High-risk or unverifiable findings require sign-off by an AUTHORISED_REVIEWER."
            )

        unresolved_violations = [
            f for f in audit.findings if f.verification_status != VerificationStatus.SUPPORTED
        ]
        if decision == "APPROVE" and unresolved_violations and not (override_justification and override_justification.strip()):
            raise ValueError(
                "Approving a draft with flagged violations or unverified claims requires a non-empty override_justification."
            )

        new_status = AuditStatus.APPROVED if decision == "APPROVE" else AuditStatus.CHANGES_REQUESTED
        now_utc = datetime.now(timezone.utc).isoformat()

        evidence_ids = sorted(
            {f.evidence_reference.reference_id for f in audit.findings if f.evidence_reference is not None}
        )
        findings_serialized = json.dumps(
            [f.model_dump(mode="json") for f in audit.findings], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        output_hash = f"sha256:{hashlib.sha256(findings_serialized).hexdigest()}"

        snapshot_id = f"SNAP-{uuid.uuid4().hex[:8].upper()}"
        canonical_snapshot_payload = {
            "snapshot_id": snapshot_id,
            "audit_id": audit.audit_id,
            "org_id": audit.org_id,
            "campaign_id": audit.campaign_id,
            "content_sha256_hash": audit.document_revision_hash,
            "brand_constitution_version": "1.0",
            "facts_vault_version": "1.0",
            "rule_engine_version": "0.2.0",
            "router_config_version": "mandatory-v1",
            "retrieved_evidence_ids": evidence_ids,
            "audit_output_sha256_hash": output_hash,
            "approval_state": new_status.value,
            "approver_role": actor_role.value,
            "approved_at_utc": now_utc,
            "hmac_key_id": settings.hmac_key_id,
            "previous_snapshot_hmac": self._last_snapshot_hmac,
        }
        canonical_bytes = json.dumps(canonical_snapshot_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(
            settings.hmac_signing_secret.encode("utf-8"),
            canonical_bytes,
            hashlib.sha256,
        ).hexdigest()

        snapshot = AuditSnapshotRecord(
            **canonical_snapshot_payload,
            review_notes=override_justification,
            snapshot_hmac_signature=signature,
        )
        self._last_snapshot_hmac = signature

        updated_audit = audit.model_copy(
            update={
                "overall_status": new_status,
                "latest_snapshot": snapshot,
            }
        )
        self._audits[audit_id] = updated_audit
        return updated_audit


orchestrator = VerityMoEOrchestrator()