from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from job_monitor.models.job import Job


SENIORITY_KEYWORDS = ("lead", "leader", "director", "manager", "mgr", "senior", "sr", "staff", "president")


def _should_include_job(job: Job) -> bool:
    title = job.title.lower()
    return not any(keyword in title for keyword in SENIORITY_KEYWORDS)


def render_new_jobs_email(jobs: Iterable[Job]) -> tuple[str, str]:
    grouped: dict[str, list[Job]] = defaultdict(list)
    for job in jobs:
        if _should_include_job(job):
            grouped[job.company].append(job)

    subject = f"New jobs found: {sum(len(items) for items in grouped.values())}"
    lines: list[str] = ["NEW JOBS FOUND", ""]

    for company in sorted(grouped):
        lines.append(f"## {company}")
        for job in sorted(grouped[company], key=lambda item: (item.title.lower(), item.location.lower(), item.url)):
            lines.append(job.title)
            if job.location:
                lines.append(f"Location: {job.location}")
            lines.append(f"URL: {job.url}")
            lines.append("")

    return subject, "\n".join(lines).rstrip() + "\n"
