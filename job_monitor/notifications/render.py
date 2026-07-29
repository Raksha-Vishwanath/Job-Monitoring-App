from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from job_monitor.models.job import Job


def render_new_jobs_email(jobs: Iterable[Job]) -> tuple[str, str]:
    grouped: dict[str, list[Job]] = defaultdict(list)
    for job in jobs:
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
