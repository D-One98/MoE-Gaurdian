from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ExecutionState(str, Enum):
    OK = "OK"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    ERROR = "ERROR"


class FindingType(str, Enum):
    DETERMINISTIC_VIOLATION = "DETERMINISTIC_VIOLATION"
    FACTUAL_CLAIM = "FACTUAL_CLAIM"
    TONE_MESSAGING = "TONE_MESSAGING"
    VISUAL_A11Y_SUBSET = "VISUAL_A11Y_SUBSET"


class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIABLE = "UNVERIFIABLE"
    NOT_CLAIM_APPLICABLE = "NOT_CLAIM_APPLICABLE"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AnchorResolutionStatus(str, Enum):
    RESOLVED_UNIQUE = "RESOLVED_UNIQUE"
    AMBIGUOUS_FALLBACK_TO_BLOCK = "AMBIGUOUS_FALLBACK_TO_BLOCK"
    UNRESOLVED_SIDEBAR_ONLY = "UNRESOLVED_SIDEBAR_ONLY"


class DemoRole(str, Enum):
    CREATOR = "CREATOR"
    BRAND_MANAGER = "BRAND_MANAGER"
    AUTHORISED_REVIEWER = "AUTHORISED_REVIEWER"
    WORKSPACE_ADMIN = "WORKSPACE_ADMIN"


class RuleCategory(str, Enum):
    BANNED_TERM = "BANNED_TERM"
    BRAND_CASING = "BRAND_CASING"
    MANDATORY_DISCLAIMER = "MANDATORY_DISCLAIMER"
    NUMERIC_BOUND = "NUMERIC_BOUND"


class BrandRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    category: RuleCategory
    title: str
    description: str
    mandatory_flag: bool = True
    severity: Severity
    pattern_or_target: str
    expected_replacement: Optional[str] = None
    numeric_max: Optional[float] = None
    numeric_unit: Optional[str] = None
    document_id: str = "DOC-BRAND-CONSTITUTION-V1"
    document_name: str = "Sample_Brand_Guidelines_v1.pdf"
    verified_page_or_row: int = 1
    version: str = "1.0"
    campaign_scope: str = "GLOBAL"


class ApprovedFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str
    topic_key: str
    subject_keywords: List[str]
    canonical_text: str
    approved_numeric_value: float
    numeric_unit: str
    comparator: str = "up_to"
    required_conditions: List[str]
    prohibited_overstatements: List[str] = Field(default_factory=list)
    document_id: str = "DOC-APPROVED-FACTS-V1"
    document_name: str = "Sample_Approved_Facts_Vault_v1.csv"
    verified_page_or_row: int = 1
    version: str = "1.0"


class ContentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_block_id: str = Field(..., min_length=1, description="Stable block ID from canonical editor structure")
    text: str = Field(..., min_length=1, description="Text content of the block")

    @field_validator("document_block_id", "text")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be blank or whitespace only.")
        return v


class EvidenceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(..., description="BRAND_RULE or APPROVED_FACT")
    reference_id: str
    document_id: str
    document_name: str
    verified_page_or_row: int
    canonical_excerpt_from_db: str


class BackendRevalidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assigned_by: str = "BACKEND_COORDINATOR"
    executed_checks: Dict[str, Any]
    candidate_verification_status: VerificationStatus
    revalidation_passed: bool


class RewriteCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    suggested_text: str
    backend_revalidation: BackendRevalidationResult


class UnifiedFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    expert_engine: str
    execution_state: ExecutionState
    finding_type: FindingType
    severity: Severity
    verification_status: VerificationStatus
    document_block_id: Optional[str] = None
    matched_text: Optional[str] = None
    prefix_context: Optional[str] = None
    suffix_context: Optional[str] = None
    anchor_resolution_status: AnchorResolutionStatus = AnchorResolutionStatus.RESOLVED_UNIQUE
    explanation: str
    evidence_reference: Optional[EvidenceReference] = None
    rewrite_candidate: Optional[RewriteCandidate] = None
    human_review_required: bool = True


class EngineExecutionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expert_engine: str
    mandatory_enforced: bool
    execution_state: ExecutionState
    findings_count: int
    notes: Optional[str] = None


class AuditCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    campaign_id: str = Field(default="CAMP-DEMO-2026", min_length=1)
    submitted_by_role: DemoRole = DemoRole.CREATOR
    blocks: List[ContentBlock] = Field(..., min_length=1)
    alt_text: Optional[str] = None


class AuditStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    READY_FOR_MANAGER_APPROVAL = "READY_FOR_MANAGER_APPROVAL"
    ESCALATED_TO_AUTHORISED_REVIEWER = "ESCALATED_TO_AUTHORISED_REVIEWER"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


class AuditSnapshotRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    audit_id: str
    org_id: str
    campaign_id: str
    content_sha256_hash: str
    brand_constitution_version: str
    facts_vault_version: str
    rule_engine_version: str
    router_config_version: str
    retrieved_evidence_ids: List[str]
    audit_output_sha256_hash: str
    approval_state: AuditStatus
    approver_role: DemoRole
    review_notes: Optional[str] = None
    approved_at_utc: str
    hmac_key_id: str
    previous_snapshot_hmac: str
    snapshot_hmac_signature: str


class AuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_id: str
    org_id: str
    campaign_id: str
    submitted_by_role: DemoRole
    document_revision_hash: str
    overall_status: AuditStatus
    human_review_required: bool
    mandatory_policies_enforced: bool
    engine_executions: List[EngineExecutionRecord]
    findings: List[UnifiedFinding]
    blocks: List[ContentBlock]
    ai_disclosure_log: Dict[str, Any]
    latest_snapshot: Optional[AuditSnapshotRecord] = None
    created_at_utc: str


class ReviewDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_role: DemoRole
    decision: str = Field(..., pattern="^(APPROVE|REQUEST_CHANGES)$")
    override_justification: Optional[str] = None