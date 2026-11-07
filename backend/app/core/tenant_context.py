import os
import re
from dataclasses import dataclass
from typing import Optional
from fastapi import Header, HTTPException, status
from app.services.seed_data import DEMO_ORG_ID

ORG_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,64}$")


@dataclass(frozen=True)
class TenantContext:
    org_id: str
    user_id: str
    is_demo_fallback: bool
    auth_mode: str


def get_tenant_context(
    authorization: Optional[str] = Header(default=None),
    x_demo_org_id: Optional[str] = Header(default=None, alias="X-Demo-Org-Id"),
) -> TenantContext:
    """
    Server-side tenant resolution boundary.
    - Never trusts arbitrary org_id fields inside request bodies.
    - When REQUIRE_VERIFIED_TENANT_AUTH=true, rejects requests unless a verified bearer token is present.
    - Note: Full Supabase JWKS cryptographic verification and server-side membership table lookup
      remain pending external Supabase project credentials. In local/demo evaluation mode,
      X-Demo-Org-Id allows isolated multi-tenant testing without cross-tenant data leakage.
    """
    require_auth = os.getenv("REQUIRE_VERIFIED_TENANT_AUTH", "false").lower() == "true"

    if require_auth:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "UNAUTHORIZED_TENANT_CONTEXT",
                    "message": "Missing Bearer token while REQUIRE_VERIFIED_TENANT_AUTH is enabled.",
                },
            )
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": "SUPABASE_JWT_VERIFIER_NOT_CONFIGURED",
                "message": "Supabase JWKS/membership verification is not yet configured with live credentials.",
            },
        )

    if x_demo_org_id is not None:
        cleaned_org = x_demo_org_id.strip()
        if not ORG_ID_PATTERN.match(cleaned_org):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_ORG_ID_HEADER",
                    "message": "X-Demo-Org-Id must be 3-64 alphanumeric, dash, or underscore characters.",
                },
            )
        return TenantContext(
            org_id=cleaned_org,
            user_id="demo-admin-sim",
            is_demo_fallback=True,
            auth_mode="DEMO_HEADER_SCOPED_SIMULATION",
        )

    return TenantContext(
        org_id=DEMO_ORG_ID,
        user_id="demo-default-user",
        is_demo_fallback=True,
        auth_mode="DEMO_DEFAULT_ORG_SIMULATION",
    )