// ============================================================================
// CLEARLY LABELLED MOCK ADAPTER FOR PRE-INTEGRATION DEVELOPMENT (Rule #9)
// Strictly adheres to shared/contracts.ts without inventing API response fields
// ============================================================================

import type {
  AuditCreateRequest,
  AuditResponse,
  ContentBlock,
  DemoRole,
  ReviewDecisionRequest,
} from '../types/contracts';

export const INITIAL_CONTENT_BLOCKS: ContentBlock[] = [
  {
    document_block_id: 'blk-paragraph-01',
    text: 'Introducing Inkloom.ai: Unmatched Enterprise Governance at Scale.',
  },
  {
    document_block_id: 'blk-paragraph-02',
    text: 'Experience uninterrupted productivity with 12 hours guaranteed battery on a single charge.',
  },
  {
    document_block_id: 'blk-paragraph-03',
    text: 'Built for distributed teams with #1 globally ranked neural compliance speed.',
  },
];

export const INITIAL_MOCK_AUDIT_RESPONSE: AuditResponse = {
  audit_id: 'AUD-2026-0042',
  org_id: 'org-inkloom-demo',
  campaign_id: 'camp-q4-launch',
  submitted_by_role: 'CREATOR',
  document_revision_hash: 'sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
  overall_status: 'ESCALATED_TO_AUTHORISED_REVIEWER',
  human_review_required: true,
  mandatory_policies_enforced: true,
  blocks: INITIAL_CONTENT_BLOCKS,
  engine_executions: [
    {
      expert_engine: 'RuleGuard',
      mandatory_enforced: true,
      execution_state: 'OK',
      findings_count: 1,
      notes: 'Deterministic regex and terminology bounds evaluated.',
    },
    {
      expert_engine: 'ClaimGuard',
      mandatory_enforced: true,
      execution_state: 'OK',
      findings_count: 2,
      notes: 'Evaluated factual claims against Approved Facts Vault.',
    },
    {
      expert_engine: 'VisualGuard',
      mandatory_enforced: true,
      execution_state: 'INSUFFICIENT_DATA',
      findings_count: 1,
      notes: 'Complex background gradient detected; escalated for human check.',
    },
    {
      expert_engine: 'VoiceGuard',
      mandatory_enforced: false,
      execution_state: 'OK',
      findings_count: 0,
      notes: 'On-demand surgical rewrite candidates generated and revalidated.',
    },
  ],
  findings: [
    {
      finding_id: 'FND-2026-01',
      expert_engine: 'RuleGuard',
      execution_state: 'OK',
      finding_type: 'DETERMINISTIC_VIOLATION',
      severity: 'MEDIUM',
      verification_status: 'NOT_CLAIM_APPLICABLE',
      document_block_id: 'blk-paragraph-01',
      matched_text: 'Inkloom.ai',
      prefix_context: 'Introducing ',
      suffix_context: ': Unmatched Enterprise',
      anchor_resolution_status: 'RESOLVED_UNIQUE',
      explanation:
        'Violates official brand casing rule. Always write "Inkloom AI" with a space and uppercase AI.',
      evidence_reference: {
        source_type: 'BRAND_RULE',
        reference_id: 'RULE-TERM-01',
        document_id: 'DOC-BRAND-2026-V1',
        document_name: 'Brand_Guidelines_2026.pdf',
        verified_page_or_row: 2,
        canonical_excerpt_from_db:
          'Official brand name is "Inkloom AI". Do not use domain-style "Inkloom.ai" in prose.',
      },
      rewrite_candidate: {
        candidate_id: 'RW-01',
        suggested_text: 'Introducing Inkloom AI: Enterprise Governance at Scale.',
        backend_revalidation: {
          assigned_by: 'BACKEND_COORDINATOR',
          executed_checks: {
            RuleGuard_execution_state: 'OK',
            RuleGuard_violations_count: 0,
            VoiceGuard_recursive_call: 'SKIPPED_BY_DESIGN',
          },
          candidate_verification_status: 'NOT_CLAIM_APPLICABLE',
          revalidation_passed: true,
        },
      },
      human_review_required: false,
    },
    {
      finding_id: 'FND-2026-02',
      expert_engine: 'ClaimGuard',
      execution_state: 'OK',
      finding_type: 'FACTUAL_CLAIM',
      severity: 'HIGH',
      verification_status: 'PARTIAL',
      document_block_id: 'blk-paragraph-02',
      matched_text: '12 hours guaranteed battery',
      prefix_context: 'Experience uninterrupted productivity with ',
      suffix_context: ' on a single charge.',
      anchor_resolution_status: 'RESOLVED_UNIQUE',
      explanation:
        'The core numeric value (12 hours) aligns with FACT-BAT-02, but the required condition ("up to" under "specified laboratory testing conditions") is omitted and replaced with an unsupported "guaranteed" claim.',
      evidence_reference: {
        source_type: 'APPROVED_FACT',
        reference_id: 'FACT-BAT-02',
        document_id: 'DOC-SPEC-2026-V2',
        document_name: 'Product_Specifications_v2.pdf',
        verified_page_or_row: 4,
        canonical_excerpt_from_db:
          'Up to 12 hours under specified laboratory testing conditions.',
      },
      rewrite_candidate: {
        candidate_id: 'RW-02',
        suggested_text:
          'Experience uninterrupted productivity with up to 12 hours of battery life under specified laboratory testing conditions on a single charge.',
        backend_revalidation: {
          assigned_by: 'BACKEND_COORDINATOR',
          executed_checks: {
            RuleGuard_execution_state: 'OK',
            RuleGuard_violations_count: 0,
            ClaimGuard_execution_state: 'OK',
            VoiceGuard_recursive_call: 'SKIPPED_BY_DESIGN',
          },
          candidate_verification_status: 'SUPPORTED',
          revalidation_passed: true,
        },
      },
      human_review_required: true,
    },
    {
      finding_id: 'FND-2026-03',
      expert_engine: 'ClaimGuard',
      execution_state: 'OK',
      finding_type: 'FACTUAL_CLAIM',
      severity: 'CRITICAL',
      verification_status: 'UNVERIFIABLE',
      document_block_id: 'blk-paragraph-03',
      matched_text: '#1 globally ranked neural compliance speed',
      prefix_context: 'Built for distributed teams with ',
      suffix_context: '.',
      anchor_resolution_status: 'RESOLVED_UNIQUE',
      explanation:
        'No supporting record exists in the Approved Facts Vault for "#1 globally ranked". Unverifiable superlative claims require removal or Authorised Reviewer sign-off.',
      evidence_reference: null,
      rewrite_candidate: null,
      human_review_required: true,
    },
    {
      finding_id: 'FND-2026-04',
      expert_engine: 'VisualGuard',
      execution_state: 'INSUFFICIENT_DATA',
      finding_type: 'VISUAL_A11Y_SUBSET',
      severity: 'LOW',
      verification_status: 'NOT_CLAIM_APPLICABLE',
      document_block_id: null,
      matched_text: null,
      prefix_context: null,
      suffix_context: null,
      anchor_resolution_status: 'UNRESOLVED_SIDEBAR_ONLY',
      explanation:
        'Foreground/background luminance contrast over non-uniform image gradient returned INSUFFICIENT_DATA. Requires human visual inspection.',
      evidence_reference: null,
      rewrite_candidate: null,
      human_review_required: true,
    },
  ],
  ai_disclosure_log: {
    adapter_mode: 'MOCK_PRE_BACKEND_INTEGRATION',
    mandatory_router_enforced: true,
    specialist_engines_invoked: ['RuleGuard', 'ClaimGuard', 'VisualGuard', 'VoiceGuard'],
  },
  latest_snapshot: null,
  created_at_utc: '2026-11-06T08:45:00Z',
};

export function createMockAudit(req: AuditCreateRequest, hash: string): AuditResponse {
  return {
    ...INITIAL_MOCK_AUDIT_RESPONSE,
    audit_id: `AUD-2026-${Math.floor(1000 + Math.random() * 9000)}`,
    campaign_id: req.campaign_id || 'camp-q4-launch',
    submitted_by_role: req.submitted_by_role || 'CREATOR',
    document_revision_hash: hash,
    blocks: req.blocks,
    created_at_utc: new Date().toISOString(),
  };
}

export function submitMockReviewDecision(
  currentAudit: AuditResponse,
  req: ReviewDecisionRequest
): AuditResponse {
  const newStatus = req.decision === 'APPROVE' ? 'APPROVED' : 'CHANGES_REQUESTED';
  return {
    ...currentAudit,
    overall_status: newStatus,
    latest_snapshot: {
      snapshot_id: `SNP-2026-${Math.floor(1000 + Math.random() * 9000)}`,
      audit_id: currentAudit.audit_id,
      org_id: currentAudit.org_id,
      campaign_id: currentAudit.campaign_id,
      content_sha256_hash: currentAudit.document_revision_hash,
      brand_constitution_version: 'v1.0.0',
      facts_vault_version: 'v1.0.0',
      rule_engine_version: 'v1.0.0',
      router_config_version: 'v1.0.0',
      retrieved_evidence_ids: ['RULE-TERM-01', 'FACT-BAT-02'],
      audit_output_sha256_hash: 'sha256:mock-audit-output-digest-pending-backend',
      approval_state: newStatus,
      approver_role: req.actor_role,
      review_notes: req.override_justification || null,
      approved_at_utc: new Date().toISOString(),
      hmac_key_id: 'mock-key-unverified',
      previous_snapshot_hmac: 'GENESIS_SNAPSHOT',
      snapshot_hmac_signature: 'MOCK_SIGNATURE_NOT_CRYPTOGRAPHICALLY_VERIFIED',
    },
  };
}