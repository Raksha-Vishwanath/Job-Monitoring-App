from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class GreenhouseCollector(JobCollector):
    """Collector for Greenhouse boards using the public JSON API."""

    company: str
    board_slug: str
    page_size: int = 100
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        offset = 0
        total: int | None = None

        while True:
            payload = self._fetch_page(offset=offset)
            page_jobs = self._parse_payload(payload)
            jobs.extend(page_jobs)

            meta = payload.get("meta") if isinstance(payload, dict) else {}
            total = self._first_int(meta, "total") if isinstance(meta, dict) else total

            if len(page_jobs) < self.page_size:
                break
            if total is not None and offset + self.page_size >= total:
                break
            offset += self.page_size

        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_page(self, *, offset: int) -> dict:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_slug}/jobs?content=true&per_page={self.page_size}&page={offset // self.page_size + 1}"
        response = get_with_timeout(self._session, url, timeout=self.request_timeout)
        return json.loads(response.text)

    def _parse_payload(self, payload: dict) -> list[Job]:
        raw_jobs = payload.get("jobs") or []
        jobs: list[Job] = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "title")
            url = self._first_str(item, "absolute_url", "absoluteUrl", "url")
            if not title or not url:
                continue
            location = self._extract_location(item)
            job_id = self._extract_job_id(item, title=title, location=location, url=url)
            posted = self._extract_date(item)
            jobs.append(
                Job(
                    company=self.company,
                    job_id=job_id,
                    title=title,
                    location=location,
                    url=url,
                    date_posted=posted,
                )
            )
        return jobs

    def _extract_job_id(self, item: dict, *, title: str, location: str, url: str) -> str:
        for key in ("id", "internal_job_id", "job_id", "requisition_id"):
            value = item.get(key)
            if value not in (None, ""):
                return str(value)
        return stable_job_hash(self.company, title, location, url)

    def _extract_location(self, item: dict) -> str:
        location = item.get("location")
        if isinstance(location, dict):
            for key in ("name", "locality", "city", "region"):
                value = location.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        if isinstance(location, str) and location.strip():
            return location.strip()

        location_name = item.get("location_name")
        if isinstance(location_name, str) and location_name.strip():
            return location_name.strip()
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("updated_at", "published_at", "updatedAt", "publishedAt", "created_at"):
            value = item.get(key)
            if isinstance(value, str) and len(value) >= 10:
                try:
                    return date.fromisoformat(value[:10])
                except ValueError:
                    continue
        return None

    def _first_str(self, item: dict, *keys: str) -> str:
        for key in keys:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _first_int(self, item: dict, *keys: str) -> int | None:
        for key in keys:
            value = item.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
        return None
