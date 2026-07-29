from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from html import unescape
from typing import Any
from urllib.parse import urljoin

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


@dataclass
class AshbyCollector(JobCollector):
    company: str
    board_slug: str
    request_timeout: float = 20.0

    def __post_init__(self) -> None:
        self._session = build_session()

    def fetch_jobs(self) -> list[Job]:
        html = self._fetch_board_html()
        postings = self._extract_job_postings(html)
        jobs: list[Job] = []
        for item in postings:
            job = self._item_to_job(item)
            if job is not None:
                jobs.append(job)
        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_board_html(self) -> str:
        url = f"https://jobs.ashbyhq.com/{self.board_slug}"
        response = get_with_timeout(self._session, url, timeout=self.request_timeout)
        return response.text

    def _extract_job_postings(self, html: str) -> list[dict[str, Any]]:
        key = '"jobPostings":['
        idx = html.find(key)
        if idx == -1:
            return []
        start = idx + len('"jobPostings":')
        array_text = self._extract_json_array(html, start)
        if not array_text:
            return []
        try:
            data = json.loads(array_text)
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    def _extract_json_array(self, text: str, start_index: int) -> str | None:
        opening = text.find("[", start_index)
        if opening == -1:
            return None
        depth = 0
        in_string = False
        escaped = False
        for index in range(opening, len(text)):
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    return text[opening : index + 1]
        return None

    def _item_to_job(self, item: Any) -> Job | None:
        if not isinstance(item, dict):
            return None
        title = self._first_str(item, "title", "jobTitle", "name")
        job_id = self._first_str(item, "id")
        if not title or not job_id:
            return None
        location = self._extract_location(item)
        url = f"https://jobs.ashbyhq.com/{self.board_slug}/{job_id}"
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
        location_name = item.get("locationName")
        if isinstance(location_name, str) and location_name.strip():
            location = location_name.strip()
        else:
            location = ""
        workplace = item.get("workplaceType")
        if isinstance(workplace, str) and workplace.strip():
            workplace_label = workplace.replace("FullTime", "Full Time").replace("OnSite", "On Site")
            if location:
                return f"{location} ({workplace_label})"
            return workplace_label
        secondary = item.get("secondaryLocations")
        if isinstance(secondary, list) and secondary:
            names = [
                entry.get("locationName")
                for entry in secondary
                if isinstance(entry, dict) and isinstance(entry.get("locationName"), str) and entry["locationName"].strip()
            ]
            if names and not location:
                return ", ".join(names)
        return location

    def _extract_date(self, item: dict[str, Any]) -> date | None:
        value = item.get("createdAt") or item.get("postedAt") or item.get("publishedAt")
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
