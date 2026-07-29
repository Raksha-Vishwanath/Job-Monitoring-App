from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Job(BaseModel):
    """Normalized job record used across all collectors."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    company: str = Field(..., description="Human-readable company name")
    job_id: str = Field(..., description="Canonical identifier for the job")
    title: str = Field(..., description="Job title")
    location: str = Field(default="", description="Job location")
    url: str = Field(..., description="Canonical application URL")
    date_posted: date | None = Field(default=None, description="Posting date if available")

    @field_validator("company", "job_id", "title", "location", "url")
    @classmethod
    def _strip_strings(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

