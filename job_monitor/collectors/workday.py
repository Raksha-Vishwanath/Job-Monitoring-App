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
class WorkdayCollector(JobCollector):
    """Collector for Workday job boards using the public JSON API."""

    company: str
    base_url: str
    tenant: str
    site: str
    page_size: int = 100
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        offset = 0

        while True:
            payload = self._fetch_page(offset=offset)
            page_jobs = self._parse_payload(payload)
            jobs.extend(page_jobs)

            if len(page_jobs) < self.page_size:
                break
            offset += self.page_size

        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_page(self, *, offset: int) -> dict:
        url = f"{self.base_url}/wday/cxs/{self.tenant}/{self.site}/jobs?limit={self.page_size}&offset={offset}"
        response = get_with_timeout(self._session, url, timeout=self.request_timeout)
        return json.loads(response.text)

    def _parse_payload(self, payload: dict) -> list[Job]:
        raw_jobs = payload.get("jobPostings") or payload.get("jobs") or []
        jobs: list[Job] = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "title", "jobTitle", "jobPostingTitle", "externalTitle")
            external_path = self._first_str(item, "externalPath", "jobPostingUrl", "url")
            if not title or not external_path:
                continue

            url = external_path if external_path.startswith("http") else urljoin(self.base_url, external_path)
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
        for key in ("externalPath", "jobId", "jobPostingId", "id", "requisitionId", "requisitionNumber"):
            value = item.get(key)
            if value not in (None, ""):
                return str(value)
        return stable_job_hash(self.company, title, location, url)

    def _extract_location(self, item: dict) -> str:
        candidates = [
            item.get("locationsText"),
            item.get("locationText"),
            item.get("location"),
            item.get("locationName"),
        ]
        for value in candidates:
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                for key in ("displayName", "name", "text"):
                    nested = value.get(key)
                    if isinstance(nested, str) and nested.strip():
                        return nested.strip()
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("postedOn", "datePosted", "createdOn", "updatedOn"):
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

