import type {
  AuditCreateRequest,
  AuditResponse,
  ReviewDecisionRequest,
} from '../types/contracts';
import { apiRequest } from './api';
import {
  createMockAudit,
  submitMockReviewDecision,
} from './mockAdapter';

export const IS_MOCK_MODE =
  import.meta.env.VITE_USE_MOCK_ADAPTER !== 'false'; //set to false after backend

export async function runAuditService(
  req: AuditCreateRequest,
  computedRevisionHash: string
): Promise<AuditResponse> {
  if (IS_MOCK_MODE) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(createMockAudit(req, computedRevisionHash));
      }, 1500);
    });
  }

  return apiRequest<AuditResponse>('/audits', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function submitReviewDecisionService(
  currentAudit: AuditResponse,
  req: ReviewDecisionRequest
): Promise<AuditResponse> {
  if (IS_MOCK_MODE) {
    return Promise.resolve(submitMockReviewDecision(currentAudit, req));
  }

  return apiRequest<AuditResponse>(`/audits/${currentAudit.audit_id}/review`, {
    method: 'POST',
    body: JSON.stringify(req),
  });
}