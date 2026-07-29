from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date
from html import unescape
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session
from job_monitor.models.job import Job
from job_monitor.utils import stable_job_hash


logger = logging.getLogger(__name__)


@dataclass
class AccentureCollector(JobCollector):
    """Collector for Accenture's public job search."""

    company: str = "Accenture"
    page_size: int = 12
    request_timeout: float = 20.0
    start_url: str = "https://www.accenture.com/us-en/careers/jobsearch"

    def __post_init__(self) -> None:
        self._session = build_session()
        self._search_config: dict[str, str] | None = None

    def fetch_jobs(self) -> list[Job]:
        for payload in self._payload_variants():
            try:
                jobs = self._fetch_with_payload(payload)
                if jobs:
                    return jobs
            except Exception:  # pragma: no cover - network/runtime failures only
                logger.exception("accenture collector failed for payload variant")
        try:
            return self._fetch_from_rendered_html()
        except Exception:  # pragma: no cover - network/runtime failures only
            logger.exception("accenture collector failed to parse rendered html")
        return []

    def _payload_variants(self) -> list[dict[str, str]]:
        config = self._load_search_config()
        base = {
            "startIndex": "0",
            "maxResultSize": str(self.page_size),
            "jobKeyword": "",
            "jobCountry": config["jobCountry"],
            "jobLanguage": config["jobLanguage"],
            "countrySite": config["countrySite"],
            "searchType": "vectorSearch",
            "enableQueryBoost": "true",
            "minScore": config["minScore"],
            "getFeedbackJudgmentEnabled": "true",
            "useCleanEmbedding": "true",
            "score": "true",
            "totalHits": "true",
            "debugQuery": "false",
            "jobFilters": "[]",
        }
        payloads: list[dict[str, str]] = []
        for sort_by in ("2", "0"):
            payload = dict(base)
            payload["sortBy"] = sort_by
            payloads.append(payload)
        return payloads

    def _load_search_config(self) -> dict[str, str]:
        if self._search_config is not None:
            return self._search_config
        response = self._session.get(self.start_url, timeout=self.request_timeout, headers=self._page_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        container = soup.select_one(".rad-job-search__filters-and-cards")
        data = container.attrs if container is not None else {}
        self._search_config = {
            "jobCountry": str(data.get("data-countrycode") or "USA"),
            "jobLanguage": str(data.get("data-language-code") or "en"),
            "countrySite": str(data.get("data-countryselector") or "us-en"),
            "minScore": str(data.get("data-minscore") or "0.7"),
        }
        return self._search_config

    def _fetch_with_payload(self, payload: dict[str, str]) -> list[Job]:
        jobs: list[Job] = []
        offset = 0
        csrf_token = self._fetch_csrf_token()

        while True:
            page_payload = dict(payload)
            page_payload["startIndex"] = str(offset)
            response = self._session.post(
                "https://www.accenture.com/api/accenture/elastic/findjobs",
                files=[(key, (None, value)) for key, value in page_payload.items()],
                headers=self._request_headers(csrf_token),
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = json.loads(response.text)
            if isinstance(data, dict) and data.get("error"):
                return []

            page_jobs = self._parse_payload(data, payload)
            if not page_jobs:
                return []
            jobs.extend(page_jobs)

            total = self._extract_total(data)
            if len(page_jobs) < self.page_size:
                break
            if total is not None and offset + self.page_size >= total:
                break
            offset += self.page_size

        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _fetch_from_rendered_html(self) -> list[Job]:
        response = self._session.get(self.start_url, timeout=self.request_timeout, headers=self._page_headers())
        response.raise_for_status()
        return self._parse_rendered_html(response.text, response.url)

    def _fetch_csrf_token(self) -> str:
        response = self._session.get(self.start_url, timeout=self.request_timeout, headers=self._page_headers())
        response.raise_for_status()
        token = self._extract_token_from_html(response.text)
        if token:
            return token
        for cookie_name in ("CSRF-Token", "csrf-token", "csrftoken", "csrf"):
            cookie_value = self._session.cookies.get(cookie_name)
            if cookie_value:
                return cookie_value
        return ""

    def _request_headers(self, csrf_token: str) -> dict[str, str]:
        headers = self._page_headers()
        if csrf_token:
            headers["CSRF-Token"] = csrf_token
        return headers

    def _page_headers(self) -> dict[str, str]:
        return {
            "Origin": "https://www.accenture.com",
            "Referer": self.start_url,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json,text/plain,*/*",
        }

    def _extract_token_from_html(self, html: str) -> str:
        patterns = [
            r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']csrf-token["\']',
            r'<input[^>]+name=["\']csrf-token["\'][^>]+value=["\']([^"\']+)["\']',
            r'<input[^>]+value=["\']([^"\']+)["\'][^>]+name=["\']csrf-token["\']',
            r'csrfToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'CSRF-Token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.I)
            if match:
                return unescape(match.group(1)).strip()
        return ""

    def _parse_payload(self, payload: object, config: dict[str, str]) -> list[Job]:
        if isinstance(payload, dict):
            candidates = payload.get("data") or payload.get("documents") or payload.get("jobs") or []
        else:
            candidates = []

        jobs: list[Job] = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            title = self._first_str(item, "title", "jobTitle")
            raw_url = self._first_str(item, "jobDetailUrl", "jobUrl", "url", "absoluteUrl")
            if not title or not raw_url:
                continue
            url = urljoin("https://www.accenture.com", raw_url.replace("{0}", config["countrySite"]))
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

    def _parse_rendered_html(self, html: str, base_url: str) -> list[Job]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.rad-filters-vertical__job-card")
        jobs: list[Job] = []
        for card in cards:
            title_tag = card.select_one("h3.rad-filters-vertical__job-card-title")
            link_tag = card.select_one("a.rad-filters-vertical__job-card-content-link-button[href]")
            details_tag = card.select_one(".rad-filters-vertical__job-card-details")
            if title_tag is None or link_tag is None:
                continue
            title = re.sub(r"\s+", " ", title_tag.get_text(" ", strip=True)).strip()
            raw_url = link_tag.get("href", "").strip()
            if not title or not raw_url:
                continue
            url = urljoin(base_url, raw_url)
            location = ""
            if details_tag is not None:
                location_tag = details_tag.select_one(".rad-filters-vertical__job-card-details-location")
                if location_tag is not None:
                    location = re.sub(r"\s+", " ", location_tag.get_text(" ", strip=True)).strip()
            job_id = self._extract_job_id_from_card(card, title=title, location=location, url=url)
            posted = self._extract_date_from_card(card)
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
        unique: dict[str, Job] = {}
        for job in jobs:
            unique.setdefault(job.job_id, job)
        return list(unique.values())

    def _extract_total(self, payload: object) -> int | None:
        if not isinstance(payload, dict):
            return None
        total_hits = payload.get("totalHits")
        if isinstance(total_hits, dict):
            value = total_hits.get("total")
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
        return None

    def _extract_job_id_from_card(self, card, *, title: str, location: str, url: str) -> str:
        for key in ("data-job-id", "job-id", "id"):
            value = card.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        title_tag = card.select_one(".rad-filters-vertical__job-card-content-job-number-dynamic-text")
        if title_tag is not None:
            value = re.sub(r"\s+", " ", title_tag.get_text(" ", strip=True)).strip()
            if value:
                return value
        return self._extract_job_id_from_url_or_hash(url, title, location)

    def _extract_date_from_card(self, card) -> date | None:
        date_tag = card.select_one(".rad-filters-vertical__job-card-content-job-posted-date-dynamic-text")
        if date_tag is None:
            return None
        raw = re.sub(r"\s+", " ", date_tag.get_text(" ", strip=True)).strip()
        if not raw:
            return None
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", raw)
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                return None
        return None

    def _extract_job_id_from_url_or_hash(self, url: str, title: str, location: str) -> str:
        match = re.search(r"[?&]id=([^&]+)", url)
        if match:
            return unescape(match.group(1))
        return stable_job_hash(self.company, title, location, url)

    def _extract_job_id(self, item: dict, *, title: str, location: str, url: str) -> str:
        for key in ("requisitionId", "jobID", "jobId", "guid", "id"):
            value = item.get(key)
            if value not in (None, ""):
                return str(value)
        return stable_job_hash(self.company, title, location, url)

    def _extract_location(self, item: dict) -> str:
        location = item.get("location")
        if isinstance(location, list) and location:
            first = location[0]
            if isinstance(first, str) and first.strip():
                return first.strip()
        if isinstance(location, str) and location.strip():
            return location.strip()
        for key in ("jobLocation", "locationText", "locationName"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _extract_date(self, item: dict) -> date | None:
        for key in ("postedDate", "publishedDate", "postedDateText"):
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
