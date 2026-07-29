from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    db_path: Path
    smtp_host: str | None
    smtp_port: int | None
    smtp_username: str | None
    smtp_password: str | None
    email_from: str | None
    email_to: str | None


def load_config() -> AppConfig:
    root = Path(__file__).resolve().parents[1]
    db_path = Path(os.getenv("JOB_DB_PATH", root / "data" / "jobs.sqlite3"))
    smtp_port = os.getenv("SMTP_PORT")
    return AppConfig(
        db_path=db_path,
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(smtp_port) if smtp_port else None,
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        email_from=os.getenv("EMAIL_FROM"),
        email_to=os.getenv("EMAIL_TO"),
    )

