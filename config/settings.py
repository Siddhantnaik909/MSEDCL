"""Environment-backed settings for the quality audit application."""

import os
import secrets
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_environment():
    """Load values from the project .env file without overriding process values."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return

    with env_file.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    secret_key: str
    database_path: str
    max_upload_mb: int

    @classmethod
    def from_environment(cls):
        secret_key = os.environ.get("APP_SECRET_KEY")
        if not secret_key:
            secret_key = secrets.token_hex(32)
            os.environ["APP_SECRET_KEY"] = secret_key

        return cls(
            secret_key=secret_key,
            database_path=os.environ.get("DATABASE_PATH", "quality_audit.db"),
            max_upload_mb=int(os.environ.get("MAX_UPLOAD_MB", "25")),
        )


load_environment()
settings = Settings.from_environment()
