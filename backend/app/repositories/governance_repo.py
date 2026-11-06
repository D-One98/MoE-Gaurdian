import json
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.orm_models import (
    BrandRuleModel,
    ApprovedFactModel,
    AuditRecordModel,
    AuditFindingModel,
    ReviewSnapshotModel,
)
from app.schemas.contracts import (
    BrandRule,
    RuleCategory,
    Severity,
    ApprovedFact,
    AuditResponse,
    AuditStatus,
    DemoRole,
    ContentBlock,
    EngineExecutionRecord,
    UnifiedFinding,
    ExecutionState,
    FindingType,
    VerificationStatus,
    AnchorResolutionStatus,
    EvidenceReference,
    RewriteCandidate,
    AuditSnapshotRecord,
)
from app.services.seed_data import (
    DEMO_ORG_ID,
    get_demo_brand_rules,
    get_demo_approved_facts,
)

GENESIS_HMAC = "GENESIS_SNAPSHOT_0000000000000000"


class DuplicateResourceError(Exception):
    pass


class GovernanceRepository:
    def __init__(self, db: Session, org_id: str = DEMO_ORG_ID) -> None:
        self.db = db
        self.org_id = org_id

    def ensure_demo_seed_data(self) -> None:
        try:
            for rule in get_demo_brand_rules():
                exists = self.db.execute(
                    select(BrandRuleModel).where(BrandRuleModel.rule_id == rule.rule_id)
                ).scalar_one_or_none()
                if exists is None:
                    self.db.add(
                        BrandRuleModel(
                            rule_id=rule.rule_id,
                            org_id=self.org_id,
                            category=rule.category.value,
                            title=rule.title,
                            description=rule.description,
                            mandatory_flag=rule.mandatory_flag,
                            severity=rule.severity.value,
                            pattern_or_target=rule.pattern_or_target,
                            expected_replacement=rule.expected_replacement,
                            numeric_max=rule.numeric_max,
                            numeric_unit=rule.numeric_unit,
                            document_id=rule.document_id,
                            document_name=rule.document_name,
                            verified_page_or_row=rule.verified_page_or_row,
                            version=rule.version,
                            campaign_scope=rule.campaign_scope,
                            is_custom=False,
                        )
                    )

            for fact in get_demo_approved_facts():
                exists = self.db.execute(
                    select(ApprovedFactModel).where(ApprovedFactModel.fact_id == fact.fact_id)
                ).scalar_one_or_none()
                if exists is None:
                    self.db.add(
                        ApprovedFactModel(
                            fact_id=fact.fact_id,
                            org_id=self.org_id,
                            topic_key=fact.topic_key,
                            subject_keywords_json=json.dumps(fact.subject_keywords),
                            canonical_text=fact.canonical_text,
                            approved_numeric_value=fact.approved_numeric_value,
                            numeric_unit=fact.numeric_unit,
                            comparator=fact.comparator,
                            required_conditions_json=json.dumps(fact.required_conditions),
                            prohibited_overstatements_json=json.dumps(fact.prohibited_overstatements),
                            document_id=fact.document_id,
                            document_name=fact.document_name,
                            verified_page_or_row=fact.verified_page_or_row,
                            version=fact.version,
                            is_custom=False,
                        )
                    )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    @staticmethod
    def _to_brand_rule_schema(m: BrandRuleModel) -> BrandRule:
        return BrandRule(
            rule_id=m.rule_id,
            category=RuleCategory(m.category),
            title=m.title,
            description=m.description,
            mandatory_flag=m.mandatory_flag,
            severity=Severity(m.severity),
            pattern_or_target=m.pattern_or_target,
            expected_replacement=m.expected_replacement,
            numeric_max=m.numeric_max,
            numeric_unit=m.numeric_unit,
            document_id=m.document_id,
            document_name=m.document_name,
            verified_page_or_row=m.verified_page_or_row,
            version=m.version,
            campaign_scope=m.campaign_scope,
        )

    @staticmethod
    def _to_approved_fact_schema(m: ApprovedFactModel) -> ApprovedFact:
        return ApprovedFact(
            fact_id=m.fact_id,
            topic_key=m.topic_key,
            subject_keywords=json.loads(m.subject_keywords_json),
            canonical_text=m.canonical_text,
            approved_numeric_value=m.approved_numeric_value,
            numeric_unit=m.numeric_unit,
            comparator=m.comparator,
            required_conditions=json.loads(m.required_conditions_json),
            prohibited_overstatements=json.loads(m.prohibited_overstatements_json),
            document_id=m.document_id,
            document_name=m.document_name,
            verified_page_or_row=m.verified_page_or_row,
            version=m.version,
        )

    def list_rules(self) -> List[BrandRule]:
        self.ensure_demo_seed_data()
        rows = (
            self.db.execute(
                select(BrandRuleModel)
                .where(BrandRuleModel.org_id == self.org_id)
                .order_by(BrandRuleModel.id.asc())
            )
            .scalars()
            .all()
        )
        return [self._to_brand_rule_schema(r) for r in rows]

    def create_rule(self, rule: BrandRule) -> BrandRule:
        self.ensure_demo_seed_data()
        existing = self.db.execute(
            select(BrandRuleModel).where(BrandRuleModel.rule_id == rule.rule_id)
        ).scalar_one_or_none()
        if existing is not None:
            raise DuplicateResourceError(f"Brand rule with rule_id '{rule.rule_id}' already exists.")

        model = BrandRuleModel(
            rule_id=rule.rule_id,
            org_id=self.org_id,
            category=rule.category.value,
            title=rule.title,
            description=rule.description,
            mandatory_flag=rule.mandatory_flag,
            severity=rule.severity.value,
            pattern_or_target=rule.pattern_or_target,
            expected_replacement=rule.expected_replacement,
            numeric_max=rule.numeric_max,
            numeric_unit=rule.numeric_unit,
            document_id=rule.document_id,
            document_name=rule.document_name,
            verified_page_or_row=rule.verified_page_or_row,
            version=rule.version,
            campaign_scope=rule.campaign_scope,
            is_custom=True,
        )
        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_brand_rule_schema(model)
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateResourceError(f"Duplicate rule_id '{rule.rule_id}'.") from exc
        except Exception:
            self.db.rollback()
            raise

    def list_facts(self) -> List[ApprovedFact]:
        self.ensure_demo_seed_data()
        rows = (
            self.db.execute(
                select(ApprovedFactModel)
                .where(ApprovedFactModel.org_id == self.org_id)
                .order_by(ApprovedFactModel.id.asc())
            )
            .scalars()
            .all()
        )
        return [self._to_approved_fact_schema(f) for f in rows]

    def create_fact(self, fact: ApprovedFact) -> ApprovedFact:
        self.ensure_demo_seed_data()
        existing = self.db.execute(
            select(ApprovedFactModel).where(ApprovedFactModel.fact_id == fact.fact_id)
        ).scalar_one_or_none()
        if existing is not None:
            raise DuplicateResourceError(f"Approved fact with fact_id '{fact.fact_id}' already exists.")

        model = ApprovedFactModel(
            fact_id=fact.fact_id,
            org_id=self.org_id,
            topic_key=fact.topic_key,
            subject_keywords_json=json.dumps(fact.subject_keywords),
            canonical_text=fact.canonical_text,
            approved_numeric_value=fact.approved_numeric_value,
            numeric_unit=fact.numeric_unit,
            comparator=fact.comparator,
            required_conditions_json=json.dumps(fact.required_conditions),
            prohibited_overstatements_json=json.dumps(fact.prohibited_overstatements),
            document_id=fact.document_id,
            document_name=fact.document_name,
            verified_page_or_row=fact.verified_page_or_row,
            version=fact.version,
            is_custom=True,
        )
        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_approved_fact_schema(model)
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateResourceError(f"Duplicate fact_id '{fact.fact_id}'.") from exc
        except Exception:
            self.db.rollback()
            raise

    def save_audit(self, audit: AuditResponse) -> AuditResponse:
        try:
            record = AuditRecordModel(
                audit_id=audit.audit_id,
                org_id=audit.org_id,
                campaign_id=audit.campaign_id,
                submitted_by_role=audit.submitted_by_role.value,
                document_revision_hash=audit.document_revision_hash,
                overall_status=audit.overall_status.value,
                human_review_required=audit.human_review_required,
                mandatory_policies_enforced=audit.mandatory_policies_enforced,
                blocks_json=json.dumps([b.model_dump(mode="json") for b in audit.blocks]),
                engine_executions_json=json.dumps([e.model_dump(mode="json") for e in audit.engine_executions]),
                ai_disclosure_log_json=json.dumps(audit.ai_disclosure_log),
                created_at_utc=audit.created_at_utc,
            )
            for f in audit.findings:
                record.findings.append(
                    AuditFindingModel(
                        audit_id=audit.audit_id,
                        finding_id=f.finding_id,
                        expert_engine=f.expert_engine,
                        execution_state=f.execution_state.value,
                        finding_type=f.finding_type.value,
                        severity=f.severity.value,
                        verification_status=f.verification_status.value,
                        document_block_id=f.document_block_id,
                        matched_text=f.matched_text,
                        prefix_context=f.prefix_context,
                        suffix_context=f.suffix_context,
                        anchor_resolution_status=f.anchor_resolution_status.value,
                        explanation=f.explanation,
                        evidence_reference_json=(
                            json.dumps(f.evidence_reference.model_dump(mode="json"))
                            if f.evidence_reference
                            else None
                        ),
                        rewrite_candidate_json=(
                            json.dumps(f.rewrite_candidate.model_dump(mode="json"))
                            if f.rewrite_candidate
                            else None
                        ),
                        human_review_required=f.human_review_required,
                    )
                )
            self.db.add(record)
            self.db.commit()
            return self.get_audit(audit.audit_id)  # type: ignore[return-value]
        except Exception:
            self.db.rollback()
            raise

    def get_audit(self, audit_id: str) -> Optional[AuditResponse]:
        record = self.db.execute(
            select(AuditRecordModel).where(
                AuditRecordModel.audit_id == audit_id,
                AuditRecordModel.org_id == self.org_id,
            )
        ).scalar_one_or_none()
        if record is None:
            return None

        findings: List[UnifiedFinding] = []
        for fm in record.findings:
            ev_ref = (
                EvidenceReference(**json.loads(fm.evidence_reference_json))
                if fm.evidence_reference_json
                else None
            )
            rw_cand = (
                RewriteCandidate(**json.loads(fm.rewrite_candidate_json))
                if fm.rewrite_candidate_json
                else None
            )
            findings.append(
                UnifiedFinding(
                    finding_id=fm.finding_id,
                    expert_engine=fm.expert_engine,
                    execution_state=ExecutionState(fm.execution_state),
                    finding_type=FindingType(fm.finding_type),
                    severity=Severity(fm.severity),
                    verification_status=VerificationStatus(fm.verification_status),
                    document_block_id=fm.document_block_id,
                    matched_text=fm.matched_text,
                    prefix_context=fm.prefix_context,
                    suffix_context=fm.suffix_context,
                    anchor_resolution_status=AnchorResolutionStatus(fm.anchor_resolution_status),
                    explanation=fm.explanation,
                    evidence_reference=ev_ref,
                    rewrite_candidate=rw_cand,
                    human_review_required=fm.human_review_required,
                )
            )

        latest_snap: Optional[AuditSnapshotRecord] = None
        if record.snapshots:
            sm = record.snapshots[-1]
            latest_snap = AuditSnapshotRecord(
                snapshot_id=sm.snapshot_id,
                audit_id=sm.audit_id,
                org_id=sm.org_id,
                campaign_id=sm.campaign_id,
                content_sha256_hash=sm.content_sha256_hash,
                brand_constitution_version=sm.brand_constitution_version,
                facts_vault_version=sm.facts_vault_version,
                rule_engine_version=sm.rule_engine_version,
                router_config_version=sm.router_config_version,
                retrieved_evidence_ids=json.loads(sm.retrieved_evidence_ids_json),
                audit_output_sha256_hash=sm.audit_output_sha256_hash,
                approval_state=AuditStatus(sm.approval_state),
                approver_role=DemoRole(sm.approver_role),
                review_notes=sm.review_notes,
                approved_at_utc=sm.approved_at_utc,
                hmac_key_id=sm.hmac_key_id,
                previous_snapshot_hmac=sm.previous_snapshot_hmac,
                snapshot_hmac_signature=sm.snapshot_hmac_signature,
            )

        return AuditResponse(
            audit_id=record.audit_id,
            org_id=record.org_id,
            campaign_id=record.campaign_id,
            submitted_by_role=DemoRole(record.submitted_by_role),
            document_revision_hash=record.document_revision_hash,
            overall_status=AuditStatus(record.overall_status),
            human_review_required=record.human_review_required,
            mandatory_policies_enforced=record.mandatory_policies_enforced,
            engine_executions=[EngineExecutionRecord(**e) for e in json.loads(record.engine_executions_json)],
            findings=findings,
            blocks=[ContentBlock(**b) for b in json.loads(record.blocks_json)],
            ai_disclosure_log=json.loads(record.ai_disclosure_log_json),
            latest_snapshot=latest_snap,
            created_at_utc=record.created_at_utc,
        )

    def get_latest_snapshot_hmac(self) -> str:
        last_snap = (
            self.db.execute(
                select(ReviewSnapshotModel)
                .where(ReviewSnapshotModel.org_id == self.org_id)
                .order_by(ReviewSnapshotModel.id.desc())
                .limit(1)
            )
            .scalars()
            .first()
        )
        return last_snap.snapshot_hmac_signature if last_snap is not None else GENESIS_HMAC

    def save_review_snapshot(self, audit_id: str, new_status: AuditStatus, snapshot: AuditSnapshotRecord) -> AuditResponse:
        try:
            record = self.db.execute(
                select(AuditRecordModel).where(
                    AuditRecordModel.audit_id == audit_id,
                    AuditRecordModel.org_id == self.org_id,
                )
            ).scalar_one_or_none()
            if record is None:
                raise KeyError(f"Audit '{audit_id}' not found.")

            record.overall_status = new_status.value
            snap_model = ReviewSnapshotModel(
                snapshot_id=snapshot.snapshot_id,
                audit_id=snapshot.audit_id,
                org_id=snapshot.org_id,
                campaign_id=snapshot.campaign_id,
                content_sha256_hash=snapshot.content_sha256_hash,
                brand_constitution_version=snapshot.brand_constitution_version,
                facts_vault_version=snapshot.facts_vault_version,
                rule_engine_version=snapshot.rule_engine_version,
                router_config_version=snapshot.router_config_version,
                retrieved_evidence_ids_json=json.dumps(snapshot.retrieved_evidence_ids),
                audit_output_sha256_hash=snapshot.audit_output_sha256_hash,
                approval_state=snapshot.approval_state.value,
                approver_role=snapshot.approver_role.value,
                review_notes=snapshot.review_notes,
                approved_at_utc=snapshot.approved_at_utc,
                hmac_key_id=snapshot.hmac_key_id,
                previous_snapshot_hmac=snapshot.previous_snapshot_hmac,
                snapshot_hmac_signature=snapshot.snapshot_hmac_signature,
            )
            self.db.add(snap_model)
            self.db.commit()
            return self.get_audit(audit_id)  # type: ignore[return-value]
        except Exception:
            self.db.rollback()
            raise