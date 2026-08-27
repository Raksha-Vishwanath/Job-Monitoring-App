from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class WayfairCollector(JobCollector):
    company: str
    page_url: str
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        response = self._session.post(
            "https://www.wayfair.com/a/careers/careers/job_search_data",
            json={
                "categoryIds": [],
                "teamIds": [],
                "locationIds": [],
                "countryIds": [1],
                "stateIds": [],
                "teamCategoryIds": [],
                "selectedJobTypeIds": [],
                "keywords": "",
            },
            headers={
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Referer": self.page_url,
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        payload = json.loads(response.text)
        jobs: list[Job] = []
        for item in payload.get("jobListData") or []:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "title")
            url = self._first_str(item, "applyLink", "structuredDataApplyLink")
            if not title or not url:
                continue
            location = self._extract_location(item)
            job_id = self._first_str(item, "requisitionId", "eid", "id")
            job_id = job_id or stable_job_hash(self.company, title, location, url)
            jobs.append(
                Job(
                    company=self.company,
                    job_id=job_id,
                    title=title,
                    location=location,
                    url=url,
                    date_posted=self._extract_date(item),
                )
            )
        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _extract_location(self, item: dict) -> str:
        location = item.get("location")
        if isinstance(location, dict):
            value = location.get("name")
            if isinstance(value, str) and value.strip():
                return value.strip()
        if isinstance(location, str) and location.strip():
            return location.strip()
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("lastUpdatedDate", "createdDate"):
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
            if value not in (None, ""):
                return str(value).strip()
        return ""