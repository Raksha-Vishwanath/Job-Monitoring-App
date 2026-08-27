from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class AmazonJobsCollector(JobCollector):
    company: str
    search_url: str
    page_size: int = 100
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        offset = 0
        while True:
            separator = "&" if "?" in self.search_url else "?"
            url = f"{self.search_url}{separator}offset={offset}&result_limit={self.page_size}"
            response = self._session.get(
                url,
                headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            payload = json.loads(response.text)
            page = [self._to_job(item) for item in payload.get("jobs") or []]
            jobs.extend(job for job in page if job is not None)
            if len(page) < self.page_size:
                break
            offset += self.page_size

        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _to_job(self, item: dict) -> Job | None:
        title = self._first_str(item, "title")
        path = self._first_str(item, "job_path", "job_url", "url")
        if not title or not path:
            return None
        url = path if path.startswith("http") else urljoin("https://www.amazon.jobs", path)
        location = self._first_str(item, "location", "normalized_location")
        job_id = self._first_str(item, "id", "job_id") or stable_job_hash(self.company, title, location, url)
        posted = self._date(item.get("posted_date"))
        return Job(company=self.company, job_id=job_id, title=title, location=location, url=url, date_posted=posted)

    def _date(self, value) -> date | None:
        if isinstance(value, str) and len(value) >= 10:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                pass
        return None

    def _first_str(self, item: dict, *keys: str) -> str:
        for key in keys:
            value = item.get(key)
            if value not in (None, ""):
                return str(value).strip()
        return ""
