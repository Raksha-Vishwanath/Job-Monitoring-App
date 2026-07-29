from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class LeverCollector(JobCollector):
    company: str
    board_slug: str
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        payload = self._fetch_payload()
        jobs: list[Job] = []
        for item in payload:
            job = self._item_to_job(item)
            if job is not None:
                jobs.append(job)
        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_payload(self) -> list[dict[str, Any]]:
        url = f"https://api.lever.co/v0/postings/{self.board_slug}?mode=json"
        response = get_with_timeout(self._session, url, timeout=self.request_timeout)
        data = json.loads(response.text)
        return data if isinstance(data, list) else []

    def _item_to_job(self, item: Any) -> Job | None:
        if not isinstance(item, dict):
            return None
        title = self._first_str(item, "text", "title", "jobTitle", "name")
        url = self._first_str(item, "hostedUrl", "applyUrl", "apply_url", "url")
        if not title or not url:
            return None
        location = self._extract_location(item)
        job_id = self._first_str(item, "id", "leverId")
        if not job_id:
            job_id = stable_job_hash(self.company, title, location, url)
        posted = self._extract_date(item)
        return Job(
            company=self.company,
            job_id=job_id,
            title=title,
            location=location,
            url=url,
            date_posted=posted,
        )

    def _extract_location(self, item: dict[str, Any]) -> str:
        categories = item.get("categories")
        if isinstance(categories, dict):
            value = categories.get("location")
            if isinstance(value, str) and value.strip():
                return value.strip()
        for key in ("location", "locationName", "team"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _extract_date(self, item: dict[str, Any]) -> date | None:
        value = item.get("createdAt") or item.get("created_at") or item.get("updatedAt")
        if isinstance(value, (int, float)):
            try:
                return date.fromtimestamp(value / 1000.0)
            except Exception:
                return None
        if isinstance(value, str) and len(value) >= 10:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
        return None

    def _first_str(self, item: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""
