from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

from bs4 import BeautifulSoup

from job_monitor.collectors.base import JobCollector
from job_monitor.http_client import build_session, get_with_timeout
from job_monitor.models.job import Job
from job_monitor.utils import normalize_company_slug, stable_job_hash


_COMMON_NAV_WORDS = {
    "home",
    "careers",
    "jobs",
    "job search",
    "search jobs",
    "see jobs",
    "see open jobs",
    "view job",
    "view jobs",
    "read full job description",
    "read job description",
    "job details",
    "learn more",
    "explore",
    "explore jobs",
    "apply",
    "apply now",
    "login",
    "sign in",
    "saved jobs",
    "job alerts",
}

_DATE_PATTERNS = [
    re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2}\b", re.I),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    re.compile(r"\bposted\s+(?:today|yesterday|\d+\s+days?\s+ago)\b", re.I),
]


@dataclass
class HtmlBoardCollector(JobCollector):
    company: str
    start_url: str
    job_href_patterns: list[str] = field(default_factory=list)
    next_link_texts: list[str] = field(default_factory=lambda: ["next", ">", ">>"])
    max_pages: int = 100
    request_timeout: float = 20.0
    headers: dict[str, str] | None = None

    def __post_init__(self) -> None:
        self._session = build_session()
        self._company_slug = normalize_company_slug(self.company)
        self._job_href_regexes = [re.compile(pattern, re.I) for pattern in self.job_href_patterns]

    def fetch_jobs(self) -> list[Job]:
        discovered: dict[str, Job] = {}
        seen_page_urls: set[str] = set()
        current_url = self.start_url
        page_count = 0

        while current_url and current_url not in seen_page_urls and page_count < self.max_pages:
            seen_page_urls.add(current_url)
            page_count += 1
            response = get_with_timeout(
                self._session,
                current_url,
                timeout=self.request_timeout,
                headers=self.headers,
            )
            jobs, next_url = self._parse_page(response.url, response.text)
            for job in jobs:
                discovered.setdefault(job.job_id, job)
            current_url = next_url
            if not jobs and not next_url:
                break

        return list(discovered.values())

    def _parse_page(self, base_url: str, html: str) -> tuple[list[Job], str | None]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: list[Job] = []

        for anchor in soup.find_all("a", href=True):
            title = self._extract_title(anchor)
            if not title or self._looks_like_nav(title):
                continue
            href = anchor["href"].strip()
            absolute_url = urljoin(base_url, href)
            if not self._looks_like_job_link(href, title):
                continue

            container_text = self._container_text(anchor)
            location = self._extract_location(anchor, container_text, title)
            date_posted = self._extract_date(container_text)
            job_id = self._extract_job_id(absolute_url, title, location)
            jobs.append(
                Job(
                    company=self.company,
                    job_id=job_id,
                    title=title,
                    location=location,
                    url=absolute_url,
                    date_posted=date_posted,
                )
            )

        next_url = self._find_next_url(soup, base_url)
        return jobs, next_url

    def _extract_title(self, anchor) -> str:
        heading = anchor.find(["h1", "h2", "h3", "h4", "h5", "h6"])
        if heading is not None:
            heading_text = re.sub(r"\s+", " ", heading.get_text(" ", strip=True)).strip()
            if heading_text and not self._looks_like_nav(heading_text):
                return heading_text

        text = anchor.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ""
        text = re.sub(r"^\d+\s+\d{1,2}/\d{1,2}/\d{2,4}\s+", "", text)
        text = re.sub(r"^\d+\s+", "", text)
        text = re.sub(r"\b(Save Saved|Save for Later|Pin|Apply|Learn More|See Jobs)\b$", "", text, flags=re.I).strip()
        return text

    def _looks_like_nav(self, text: str) -> bool:
        normalized = re.sub(r"\s+", " ", text).strip().lower()
        return normalized in _COMMON_NAV_WORDS or len(normalized) < 3

    def _looks_like_job_link(self, href: str, title: str) -> bool:
        href_lower = href.lower()
        if any(regex.search(href_lower) for regex in self._job_href_regexes):
            return True
        return False

    def _container_text(self, anchor) -> str:
        container = anchor.find_parent(["li", "article", "section", "div"]) or anchor.parent
        if container is None:
            return anchor.get_text(" ", strip=True)
        text = container.get_text("\n", strip=True)
        text = re.sub(r"\n+", "\n", text)
        return text

    def _extract_location(self, anchor, container_text: str, title: str) -> str:
        # Prefer explicit location labels when the board exposes them in the card markup.
        # This avoids pulling the whole card text into the title/location fields.
        container = anchor.find_parent(["li", "article", "section", "div"]) or anchor.parent
        for element in list(anchor.find_all(True)) + list(container.find_all(True) if container is not None else []):
            classes = " ".join(element.get("class", []))
            if any(token in classes.lower() for token in ("location", "city", "region", "remote")):
                value = re.sub(r"\s+", " ", element.get_text(" ", strip=True)).strip()
                if value and value != title:
                    return value

        lines = [line.strip() for line in container_text.splitlines() if line.strip()]
        candidates: list[str] = []
        for line in lines:
            if line == title:
                continue
            lowered = line.lower()
            if lowered in _COMMON_NAV_WORDS:
                continue
            if any(pattern.search(line) for pattern in _DATE_PATTERNS):
                continue
            if len(line) > 120:
                continue
            if re.search(r"\b(remote|hybrid|onsite)\b", lowered) or re.search(r"[A-Z][a-z]+, [A-Z]{2}", line):
                candidates.append(line)
            elif "," in line and len(line.split()) <= 8:
                candidates.append(line)
        return candidates[0] if candidates else ""

    def _extract_date(self, container_text: str):
        for pattern in _DATE_PATTERNS:
            match = pattern.search(container_text)
            if match:
                value = match.group(0).strip()
                try:
                    return datetime.strptime(value, "%b %d").date().replace(year=datetime.utcnow().year)
                except ValueError:
                    try:
                        return datetime.strptime(value, "%B %d").date().replace(year=datetime.utcnow().year)
                    except ValueError:
                        return None
        return None

    def _extract_job_id(self, url: str, title: str, location: str) -> str:
        path = urlparse(url).path.rstrip("/")
        parts = [part for part in path.split("/") if part]
        for part in reversed(parts):
            if part.isdigit():
                return part
        numeric = re.findall(r"\d{6,}", url)
        if numeric:
            return numeric[-1]
        return stable_job_hash(self.company, title, location, url)

    def _find_next_url(self, soup: BeautifulSoup, base_url: str) -> str | None:
        for anchor in soup.find_all("a", href=True):
            text = re.sub(r"\s+", " ", anchor.get_text(" ", strip=True)).lower()
            if text in {"next", ">", ">>", "older", "older jobs"}:
                return urljoin(base_url, anchor["href"])
        for anchor in soup.find_all("a", href=True):
            aria = (anchor.get("aria-label") or "").lower()
            rel = " ".join(anchor.get("rel", [])).lower()
            if "next" in aria or "next" in rel:
                return urljoin(base_url, anchor["href"])
        return None
