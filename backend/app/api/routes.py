from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas.contracts import (
    ApprovedFact,
    AuditCreateRequest,
    AuditResponse,
    BrandRule,
    ReviewDecisionRequest,
    DemoRole,
)
from app.services.seed_data import (
    DEMO_ORG_ID,
    DEMO_ORG_NAME,
    get_demo_sample_drafts,
)
from app.repositories.governance_repo import (
    GovernanceRepository,
    DuplicateResourceError,
)
from app.services.orchestrator import orchestrator

router = APIRouter(prefix="/api")


@router.get("/health")
def get_health():
    return {
        "status": "ok",
        "application": "MoE-GUARDIAN",
        "engine": "VERITY MoE",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/demo/workspace")
def get_demo_workspace(db: Session = Depends(get_db)):
    repo = GovernanceRepository(db, org_id=DEMO_ORG_ID)
    rules = repo.list_rules()
    facts = repo.list_facts()
    return {
        "demo_mode": True,
        "demo_notice": (
            "Public evaluation sandbox with non-sensitive sample data. "
            "Role switching is a demo-only simulation; production deployments enforce server-verified JWT authentication."
        ),
        "org_id": DEMO_ORG_ID,
        "org_name": DEMO_ORG_NAME,
        "allowed_demo_roles": [r.value for r in DemoRole],
        "rules_count": len(rules),
        "facts_count": len(facts),
        "sample_drafts": get_demo_sample_drafts(),
    }


@router.get("/brand/rules")
def list_brand_rules(db: Session = Depends(get_db)):
    repo = GovernanceRepository(db, org_id=DEMO_ORG_ID)
    return {
        "org_id": DEMO_ORG_ID,
        "brand_constitution_version": "1.0",
        "rules": repo.list_rules(),
    }


@router.post("/brand/rules", status_code=status.HTTP_201_CREATED)
def create_brand_rule(payload: BrandRule, db: Session = Depends(get_db)):
    repo = GovernanceRepository(db, org_id=DEMO_ORG_ID)
    try:
        created_rule = repo.create_rule(payload)
        return {
            "org_id": DEMO_ORG_ID,
            "brand_constitution_version": "1.0",
            "rule": created_rule,
        }
    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_RULE_ID",
                "message": str(exc),
            },
        )


@router.get("/brand/facts")
def list_brand_facts(db: Session = Depends(get_db)):
    repo = GovernanceRepository(db, org_id=DEMO_ORG_ID)
    return {
        "org_id": DEMO_ORG_ID,
        "facts_vault_version": "1.0",
        "facts": repo.list_facts(),
    }


@router.post("/brand/facts", status_code=status.HTTP_201_CREATED)
def create_brand_fact(payload: ApprovedFact, db: Session = Depends(get_db)):
    repo = GovernanceRepository(db, org_id=DEMO_ORG_ID)
    try:
        created_fact = repo.create_fact(payload)
        return {
            "org_id": DEMO_ORG_ID,
            "facts_vault_version": "1.0",
            "fact": created_fact,
        }
    except DuplicateResourceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_FACT_ID",
                "message": str(exc),
            },
        )


@router.post("/audits", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
def create_audit(payload: AuditCreateRequest, db: Session = Depends(get_db)):
    return orchestrator.run_audit(db, payload)


@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit_by_id(audit_id: str, db: Session = Depends(get_db)):
    audit = orchestrator.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "AUDIT_NOT_FOUND", "message": f"No audit found with ID '{audit_id}'."},
        )
    return audit


@router.post("/audits/{audit_id}/review", response_model=AuditResponse)
def review_audit(audit_id: str, payload: ReviewDecisionRequest, db: Session = Depends(get_db)):
    try:
        return orchestrator.record_review_decision(
            db=db,
            audit_id=audit_id,
            actor_role=payload.actor_role,
            decision=payload.decision,
            override_justification=payload.override_justification,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "AUDIT_NOT_FOUND", "message": str(exc)},
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "MAKER_CHECKER_OR_ROLE_FORBIDDEN", "message": str(exc)},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_REVIEW_TRANSITION", "message": str(exc)},
        )