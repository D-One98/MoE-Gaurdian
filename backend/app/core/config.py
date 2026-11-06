import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    app_name: str = "MoE-GUARDIAN API (Powered by VERITY MoE)"
    app_version: str = "0.2.0-round2-foundation"
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./moe_guardian_dev.db"))
    hmac_signing_secret: str = field(
        default_factory=lambda: os.getenv("HMAC_SIGNING_SECRET", "dev-only-replace-in-production-hmac-secret-key-2026")
    )
    hmac_key_id: str = field(default_factory=lambda: os.getenv("HMAC_KEY_ID", "key-v1-local"))
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "none"))
    max_image_upload_bytes: int = field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_UPLOAD_BYTES", str(5 * 1024 * 1024)))
    )
    max_image_pixels: int = field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_PIXELS", str(16_000_000)))
    )
    cors_origins: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
            if origin.strip()
        ]
    )


settings = Settings()