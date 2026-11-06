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

    rule_id: str = Field(..., min_length=3, max_length=64)
    category: RuleCategory
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    mandatory_flag: bool = True
    severity: Severity
    pattern_or_target: str = Field(..., min_length=1)
    expected_replacement: Optional[str] = None
    numeric_max: Optional[float] = None
    numeric_unit: Optional[str] = None
    document_id: str = Field(default="DOC-BRAND-CONSTITUTION-V1", min_length=1)
    document_name: str = Field(default="Sample_Brand_Guidelines_v1.pdf", min_length=1)
    verified_page_or_row: int = Field(default=1, ge=1)
    version: str = Field(default="1.0", min_length=1)
    campaign_scope: str = Field(default="GLOBAL", min_length=1)

    @field_validator(
        "rule_id",
        "title",
        "description",
        "pattern_or_target",
        "document_id",
        "document_name",
        "version",
        "campaign_scope",
    )
    @classmethod
    def validate_non_blank_rule_fields(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be blank or whitespace only.")
        return v.strip()


class ApprovedFact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str = Field(..., min_length=3, max_length=64)
    topic_key: str = Field(..., min_length=2, max_length=128)
    subject_keywords: List[str] = Field(..., min_length=1)
    canonical_text: str = Field(..., min_length=5)
    approved_numeric_value: float
    numeric_unit: str = Field(..., min_length=1, max_length=64)
    comparator: str = Field(default="up_to", pattern="^(up_to|exact|at_least)$")
    required_conditions: List[str] = Field(default_factory=list)
    prohibited_overstatements: List[str] = Field(default_factory=list)
    document_id: str = Field(default="DOC-APPROVED-FACTS-V1", min_length=1)
    document_name: str = Field(default="Sample_Approved_Facts_Vault_v1.csv", min_length=1)
    verified_page_or_row: int = Field(default=1, ge=1)
    version: str = Field(default="1.0", min_length=1)

    @field_validator(
        "fact_id",
        "topic_key",
        "canonical_text",
        "numeric_unit",
        "document_id",
        "document_name",
        "version",
    )
    @classmethod
    def validate_non_blank_fact_fields(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be blank or whitespace only.")
        return v.strip()

    @field_validator("subject_keywords")
    @classmethod
    def validate_subject_keywords(cls, v: List[str]) -> List[str]:
        cleaned = [kw.strip() for kw in v if kw and kw.strip()]
        if not cleaned:
            raise ValueError("subject_keywords must contain at least one non-blank keyword.")
        return cleaned

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

class VisualAssetInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_block_id: str = Field(default="blk-visual-asset-01", min_length=1)
    filename: str = Field(default="creative.png", min_length=1)
    mime_type: str = Field(..., min_length=1, description="Declared MIME type (image/png or image/jpeg)")
    image_base64: str = Field(..., min_length=4, description="Base64-encoded image bytes")
    alt_text: Optional[str] = None
    declared_foreground_hex: Optional[str] = Field(
        default=None, description="Optional reliably known foreground text hex (#RRGGBB)"
    )
    declared_background_hex: Optional[str] = Field(
        default=None, description="Optional reliably known background hex (#RRGGBB)"
    )

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
    visual_asset: Optional[VisualAssetInput] = None

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