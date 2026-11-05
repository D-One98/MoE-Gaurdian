from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["application"] == "MoE-GUARDIAN"
    assert data["engine"] == "VERITY MoE"


def test_demo_workspace_and_brand_endpoints():
    ws = client.get("/api/demo/workspace")
    assert ws.status_code == 200
    assert ws.json()["demo_mode"] is True
    assert len(ws.json()["sample_drafts"]) == 3

    rules = client.get("/api/brand/rules")
    assert rules.status_code == 200
    assert len(rules.json()["rules"]) >= 4

    facts = client.get("/api/brand/facts")
    assert facts.status_code == 200
    assert len(facts.json()["facts"]) >= 2


def test_ruleguard_banned_term_and_brand_casing():
    payload = {
        "campaign_id": "CAMP-TEST-01",
        "submitted_by_role": "CREATOR",
        "blocks": [
            {
                "document_block_id": "blk-1",
                "text": "AuroraGear is the world's #1 laptop with guaranteed performance.",
            }
        ],
    }
    resp = client.post("/api/audits", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["mandatory_policies_enforced"] is True

    rg_findings = [f for f in data["findings"] if f["expert_engine"] == "RuleGuard"]
    rule_ids = {f["evidence_reference"]["reference_id"] for f in rg_findings}
    assert "RULE-CASE-001" in rule_ids
    assert "RULE-TERM-001" in rule_ids
    assert "RULE-TERM-002" in rule_ids


def test_claimguard_supported_fact_matching():
    payload = {
        "campaign_id": "CAMP-TEST-02",
        "submitted_by_role": "CREATOR",
        "blocks": [
            {
                "document_block_id": "blk-clean",
                "text": "AURORAGEAR provides up to 12 hours of battery life under specified laboratory testing conditions.",
            }
        ],
    }
    resp = client.post("/api/audits", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    cg_findings = [f for f in data["findings"] if f["expert_engine"] == "ClaimGuard"]
    assert len(cg_findings) == 1
    assert cg_findings[0]["verification_status"] == "SUPPORTED"
    assert cg_findings[0]["evidence_reference"]["reference_id"] == "FACT-BAT-001"
    assert data["overall_status"] == "READY_FOR_MANAGER_APPROVAL"


def test_claimguard_missing_required_conditions_partial_and_revalidated_rewrite():
    payload = {
        "campaign_id": "CAMP-TEST-03",
        "submitted_by_role": "CREATOR",
        "blocks": [
            {
                "document_block_id": "blk-partial",
                "text": "AURORAGEAR delivers 12 hours of guaranteed battery life on a single charge!",
            }
        ],
    }
    resp = client.post("/api/audits", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    cg_findings = [f for f in data["findings"] if f["expert_engine"] == "ClaimGuard"]
    assert len(cg_findings) == 1
    finding = cg_findings[0]
    assert finding["verification_status"] == "PARTIAL"
    assert finding["evidence_reference"]["reference_id"] == "FACT-BAT-001"

    rw = finding["rewrite_candidate"]
    assert rw is not None
    assert rw["backend_revalidation"]["revalidation_passed"] is True
    assert rw["backend_revalidation"]["candidate_verification_status"] == "SUPPORTED"
    assert rw["backend_revalidation"]["executed_checks"]["RuleGuard_violations_count"] == 0


def test_claimguard_contradicted_and_unverifiable_claims():
    payload = {
        "campaign_id": "CAMP-TEST-04",
        "submitted_by_role": "CREATOR",
        "blocks": [
            {
                "document_block_id": "blk-contra",
                "text": "AURORAGEAR delivers up to 24 hours of battery life under specified laboratory testing conditions.",
            },
            {
                "document_block_id": "blk-unver",
                "text": "Our chassis is certified to survive 5000 meters of deep-ocean pressure.",
            },
        ],
    }
    resp = client.post("/api/audits", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    statuses = {
        f["document_block_id"]: f["verification_status"]
        for f in data["findings"]
        if f["expert_engine"] == "ClaimGuard"
    }
    assert statuses["blk-contra"] == "CONTRADICTED"
    assert statuses["blk-unver"] == "UNVERIFIABLE"
    assert data["overall_status"] == "ESCALATED_TO_AUTHORISED_REVIEWER"


def test_maker_checker_and_hmac_snapshot_signing():
    payload = {
        "campaign_id": "CAMP-TEST-05",
        "submitted_by_role": "CREATOR",
        "blocks": [
            {
                "document_block_id": "blk-1",
                "text": "AURORAGEAR delivers 12 hours of guaranteed battery life.",
            }
        ],
    }
    audit_id = client.post("/api/audits", json=payload).json()["audit_id"]

    creator_resp = client.post(
        f"/api/audits/{audit_id}/review",
        json={"actor_role": "CREATOR", "decision": "APPROVE", "override_justification": "Looks fine"},
    )
    assert creator_resp.status_code == 403

    missing_just_resp = client.post(
        f"/api/audits/{audit_id}/review",
        json={"actor_role": "AUTHORISED_REVIEWER", "decision": "APPROVE"},
    )
    assert missing_just_resp.status_code == 400

    ok_resp = client.post(
        f"/api/audits/{audit_id}/review",
        json={
            "actor_role": "AUTHORISED_REVIEWER",
            "decision": "APPROVE",
            "override_justification": "Approved for lab teaser with footnote.",
        },
    )
    assert ok_resp.status_code == 200
    snap = ok_resp.json()["latest_snapshot"]
    assert snap is not None
    assert snap["approval_state"] == "APPROVED"
    assert len(snap["snapshot_hmac_signature"]) == 64


def test_invalid_request_handling():
    resp = client.post("/api/audits", json={"campaign_id": "CAMP-ERR", "blocks": []})
    assert resp.status_code == 422

    not_found = client.get("/api/audits/AUD-DOESNOTEXIST")
    assert not_found.status_code == 404