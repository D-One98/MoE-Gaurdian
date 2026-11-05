import re
from typing import List, Tuple
from app.schemas.contracts import (
    BrandRule,
    RuleCategory,
    ContentBlock,
    UnifiedFinding,
    ExecutionState,
    FindingType,
    VerificationStatus,
    EvidenceReference,
    EngineExecutionRecord,
)
from app.services.anchoring import resolve_block_text_anchor


def _build_rule_evidence(rule: BrandRule) -> EvidenceReference:
    return EvidenceReference(
        source_type="BRAND_RULE",
        reference_id=rule.rule_id,
        document_id=rule.document_id,
        document_name=rule.document_name,
        verified_page_or_row=rule.verified_page_or_row,
        canonical_excerpt_from_db=rule.description,
    )


def run_rule_guard(
    blocks: List[ContentBlock],
    rules: List[BrandRule],
) -> Tuple[List[UnifiedFinding], EngineExecutionRecord]:
    findings: List[UnifiedFinding] = []
    finding_counter = 1

    try:
        for block in blocks:
            text = block.text

            for rule in rules:
                if rule.category == RuleCategory.BANNED_TERM:
                    pattern = re.compile(re.escape(rule.pattern_or_target), re.IGNORECASE)
                    for match in pattern.finditer(text):
                        matched_str = match.group(0)
                        prefix, suffix, anchor_status = resolve_block_text_anchor(
                            text, matched_str, occ_start=match.start()
                        )
                        findings.append(
                            UnifiedFinding(
                                finding_id=f"FND-RG-{finding_counter:04d}",
                                expert_engine="RuleGuard",
                                execution_state=ExecutionState.OK,
                                finding_type=FindingType.DETERMINISTIC_VIOLATION,
                                severity=rule.severity,
                                verification_status=VerificationStatus.NOT_CLAIM_APPLICABLE,
                                document_block_id=block.document_block_id,
                                matched_text=matched_str,
                                prefix_context=prefix,
                                suffix_context=suffix,
                                anchor_resolution_status=anchor_status,
                                explanation=f"Banned term '{matched_str}' violates {rule.rule_id}: {rule.description}",
                                evidence_reference=_build_rule_evidence(rule),
                                rewrite_candidate=None,
                                human_review_required=True,
                            )
                        )
                        finding_counter += 1

                elif rule.category == RuleCategory.BRAND_CASING:
                    target = rule.pattern_or_target
                    pattern = re.compile(r"\b" + re.escape(target) + r"\b", re.IGNORECASE)
                    for match in pattern.finditer(text):
                        matched_str = match.group(0)
                        if matched_str != target:
                            prefix, suffix, anchor_status = resolve_block_text_anchor(
                                text, matched_str, occ_start=match.start()
                            )
                            findings.append(
                                UnifiedFinding(
                                    finding_id=f"FND-RG-{finding_counter:04d}",
                                    expert_engine="RuleGuard",
                                    execution_state=ExecutionState.OK,
                                    finding_type=FindingType.DETERMINISTIC_VIOLATION,
                                    severity=rule.severity,
                                    verification_status=VerificationStatus.NOT_CLAIM_APPLICABLE,
                                    document_block_id=block.document_block_id,
                                    matched_text=matched_str,
                                    prefix_context=prefix,
                                    suffix_context=suffix,
                                    anchor_resolution_status=anchor_status,
                                    explanation=(
                                        f"Incorrect brand casing '{matched_str}'. "
                                        f"Rule {rule.rule_id} requires exact casing '{target}'."
                                    ),
                                    evidence_reference=_build_rule_evidence(rule),
                                    rewrite_candidate=None,
                                    human_review_required=False,
                                )
                            )
                            finding_counter += 1

                elif rule.category == RuleCategory.MANDATORY_DISCLAIMER:
                    if re.search(r"\b\d+(?:\.\d+)?\s*hours?\b", text, re.IGNORECASE) and "battery" in text.lower():
                        if rule.pattern_or_target.lower() not in text.lower():
                            prefix, suffix, anchor_status = resolve_block_text_anchor(
                                text, text.strip(), occ_start=0
                            )
                            findings.append(
                                UnifiedFinding(
                                    finding_id=f"FND-RG-{finding_counter:04d}",
                                    expert_engine="RuleGuard",
                                    execution_state=ExecutionState.OK,
                                    finding_type=FindingType.DETERMINISTIC_VIOLATION,
                                    severity=rule.severity,
                                    verification_status=VerificationStatus.NOT_CLAIM_APPLICABLE,
                                    document_block_id=block.document_block_id,
                                    matched_text=text.strip(),
                                    prefix_context=prefix,
                                    suffix_context=suffix,
                                    anchor_resolution_status=anchor_status,
                                    explanation=(
                                        f"Missing mandatory disclaimer required by {rule.rule_id}: "
                                        f"'{rule.pattern_or_target}'."
                                    ),
                                    evidence_reference=_build_rule_evidence(rule),
                                    rewrite_candidate=None,
                                    human_review_required=True,
                                )
                            )
                            finding_counter += 1

                elif rule.category == RuleCategory.NUMERIC_BOUND and rule.numeric_max is not None:
                    disc_pattern = re.compile(r"\b(\d+(?:\.\d+)?)\s*%\s*(?:off|discount)\b", re.IGNORECASE)
                    for match in disc_pattern.finditer(text):
                        val = float(match.group(1))
                        if val > rule.numeric_max:
                            matched_str = match.group(0)
                            prefix, suffix, anchor_status = resolve_block_text_anchor(
                                text, matched_str, occ_start=match.start()
                            )
                            findings.append(
                                UnifiedFinding(
                                    finding_id=f"FND-RG-{finding_counter:04d}",
                                    expert_engine="RuleGuard",
                                    execution_state=ExecutionState.OK,
                                    finding_type=FindingType.DETERMINISTIC_VIOLATION,
                                    severity=rule.severity,
                                    verification_status=VerificationStatus.NOT_CLAIM_APPLICABLE,
                                    document_block_id=block.document_block_id,
                                    matched_text=matched_str,
                                    prefix_context=prefix,
                                    suffix_context=suffix,
                                    anchor_resolution_status=anchor_status,
                                    explanation=(
                                        f"Discount claim '{matched_str}' ({val}%) exceeds maximum bound "
                                        f"of {rule.numeric_max}% defined in {rule.rule_id}."
                                    ),
                                    evidence_reference=_build_rule_evidence(rule),
                                    rewrite_candidate=None,
                                    human_review_required=True,
                                )
                            )
                            finding_counter += 1

        exec_record = EngineExecutionRecord(
            expert_engine="RuleGuard",
            mandatory_enforced=True,
            execution_state=ExecutionState.OK,
            findings_count=len(findings),
            notes="Deterministic banned-term, brand-casing, disclaimer, and numeric bound checks executed.",
        )
        return findings, exec_record

    except Exception as exc:
        return [], EngineExecutionRecord(
            expert_engine="RuleGuard",
            mandatory_enforced=True,
            execution_state=ExecutionState.ERROR,
            findings_count=0,
            notes=f"RuleGuard execution error: {type(exc).__name__}",
        )