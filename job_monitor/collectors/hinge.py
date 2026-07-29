from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class HingeCollector(JobCollector):
    company: str = "Hinge Health"
    page_url: str = "https://jobs.ashbyhq.com/hinge-health"
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        response = get_with_timeout(self._session, self.page_url, timeout=self.request_timeout)
        payload = self._extract_app_data(response.text)
        if payload is None:
            return []

        raw_jobs = (payload.get("jobBoard") or {}).get("jobPostings") or []
        jobs: list[Job] = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "title")
            if not title:
                continue
            location = self._extract_location(item)
            url = self.page_url
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

    def _extract_app_data(self, html: str) -> dict | None:
        marker = "window.__appData = "
        idx = html.find(marker)
        if idx == -1:
            return None
        start = html.find("{", idx)
        if start == -1:
            return None
        decoder = json.JSONDecoder()
        payload, _ = decoder.raw_decode(html[start:])
        return payload

    def _extract_job_id(self, item: dict, *, title: str, location: str, url: str) -> str:
        for key in ("jobRequisitionId", "jobId", "id"):
            value = item.get(key)
            if value not in (None, ""):
                return str(value)
        return stable_job_hash(self.company, title, location, url)

    def _extract_location(self, item: dict) -> str:
        for key in ("locationName", "locationExternalName", "workplaceType"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        secondary = item.get("secondaryLocations")
        if isinstance(secondary, list) and secondary:
            first = secondary[0]
            if isinstance(first, dict):
                for key in ("name", "displayName", "locationName"):
                    value = first.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("publishedDate", "updatedAt"):
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
