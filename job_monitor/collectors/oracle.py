from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class OracleCollector(JobCollector):
    """Collector for Oracle Candidate Experience public requisition feeds."""

    company: str
    site_number: str
    api_base_url: str
    job_base_url: str
    page_size: int = 200
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

            if total is None:
                total = self._extract_total(payload)

            returned = len(page_jobs)
            if returned < self.page_size:
                break
            if total is not None and offset + returned >= total:
                break
            offset += self.page_size

        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_page(self, *, offset: int) -> dict:
        url = (
            f"{self.api_base_url.rstrip('/')}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
            f"?onlyData=true&expand=requisitionList.secondaryLocations,"
            f"requisitionList.workLocation,requisitionList.otherWorkLocations,"
            f"requisitionList.requisitionFlexFields&finder=findReqs;"
            f"siteNumber={self.site_number},limit={self.page_size},offset={offset}"
        )
        last_error: Exception | None = None
        for _ in range(3):
            response = get_with_timeout(self._session, url, timeout=self.request_timeout)
            try:
                return json.loads(response.text)
            except json.JSONDecodeError as exc:
                last_error = exc
                time.sleep(0.5)
        assert last_error is not None
        raise last_error

    def _parse_payload(self, payload: dict) -> list[Job]:
        items = payload.get("items") or []
        if not items:
            return []

        search_result = items[0]
        raw_jobs = search_result.get("requisitionList") or []
        jobs: list[Job] = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "Title")
            if not title:
                continue
            location = self._extract_location(item)
            job_id = self._extract_job_id(item, title=title, location=location)
            url = self._build_job_url(job_id)
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

    def _extract_total(self, payload: dict) -> int | None:
        items = payload.get("items") or []
        if not items:
            return None
        total = items[0].get("TotalJobsCount")
        if isinstance(total, int):
            return total
        if isinstance(total, str) and total.isdigit():
            return int(total)
        return None

    def _build_job_url(self, job_id: str) -> str:
        return urljoin(self.job_base_url.rstrip("/") + "/", f"job/{job_id}")

    def _extract_job_id(self, item: dict, *, title: str, location: str) -> str:
        for key in ("Id", "JobId", "RequisitionNumber", "RequisitionId"):
            value = item.get(key)
            if value not in (None, ""):
                return str(value)
        return stable_job_hash(self.company, title, location, self.job_base_url)

    def _extract_location(self, item: dict) -> str:
        for key in ("PrimaryLocation", "WorkplaceType", "JobFamily", "JobFunction"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        work_locations = item.get("workLocation")
        if isinstance(work_locations, list) and work_locations:
            first = work_locations[0]
            if isinstance(first, dict):
                parts = [
                    first.get("TownOrCity"),
                    first.get("Region2"),
                    first.get("Country"),
                ]
                formatted = ", ".join(part.strip() for part in parts if isinstance(part, str) and part.strip())
                if formatted:
                    return formatted
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("PostedDate", "PostingEndDate"):
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
