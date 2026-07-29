from __future__ import annotations

import logging
import smtplib
from collections import defaultdict
from typing import Iterable

from job_monitor.companies.registry import build_collectors
from job_monitor.config import load_config
from job_monitor.database.db import JobDatabase
from job_monitor.logging_utils import configure_logging
from job_monitor.models.job import Job
from job_monitor.notifications.email_sender import EmailNotificationSender
from job_monitor.notifications.render import render_new_jobs_email
from job_monitor.utils import stable_job_hash


logger = logging.getLogger(__name__)


def canonicalize_jobs(jobs: Iterable[Job]) -> list[Job]:
    unique: dict[str, Job] = {}
    for job in jobs:
        job_id = job.job_id or stable_job_hash(job.company, job.title, job.location, job.url)
        if job_id not in unique:
            unique[job_id] = job.model_copy(update={"job_id": job_id})
    return list(unique.values())


def detect_new_jobs(db: JobDatabase, jobs: Iterable[Job]) -> tuple[list[Job], list[Job]]:
    normalized = canonicalize_jobs(jobs)
    seen_ids = db.existing_job_ids(job.job_id for job in normalized)
    new_jobs = [job for job in normalized if job.job_id not in seen_ids]
    return normalized, new_jobs


def run() -> int:
    configure_logging()
    config = load_config()
    db = JobDatabase(config.db_path)
    collectors = build_collectors()

    try:
        all_jobs: list[Job] = []
        for collector in collectors:
            company_name = getattr(collector, "company", collector.__class__.__name__)
            logger.info("querying company", extra={"company": company_name})
            try:
                jobs = canonicalize_jobs(collector.fetch_jobs())
                logger.info(
                    "company queried",
                    extra={
                        "company": company_name,
                        "jobs_retrieved": len(jobs),
                    },
                )
                all_jobs.extend(jobs)
            except Exception as exc:  # pragma: no cover - runtime network/remote failures
                logger.exception(
                    "company failed",
                    extra={"company": company_name, "error": str(exc)},
                )

        normalized_jobs, new_jobs = detect_new_jobs(db, all_jobs)
        db.insert_jobs(normalized_jobs)
        for company, company_jobs in _group_jobs_by_company(new_jobs).items():
            logger.info(
                "company new jobs",
                extra={"company": company, "new_jobs": len(company_jobs)},
            )
        logger.info(
            "run completed",
            extra={
                "jobs_retrieved": len(normalized_jobs),
                "new_jobs": len(new_jobs),
            },
        )

        if new_jobs:
            if not all(
                [
                    config.smtp_host,
                    config.smtp_port,
                    config.smtp_username,
                    config.smtp_password,
                    config.email_from,
                    config.email_to,
                ]
            ):
                raise RuntimeError("SMTP and email environment variables must be configured to send notifications")

            subject, body = render_new_jobs_email(new_jobs)
            sender = EmailNotificationSender(
                host=config.smtp_host or "",
                port=config.smtp_port or 0,
                username=config.smtp_username or "",
                password=config.smtp_password or "",
                email_from=config.email_from or "",
                email_to=config.email_to or "",
            )
            try:
                sender.send(subject, body)
            except smtplib.SMTPAuthenticationError as exc:
                logger.error(
                    "smtp authentication failed",
                    extra={"error": str(exc)},
                )
                return 1
            except smtplib.SMTPException as exc:
                logger.error(
                    "smtp send failed",
                    extra={"error": str(exc)},
                )
                return 1

        return 0
    finally:
        db.close()


def _group_jobs_by_company(jobs: Iterable[Job]) -> dict[str, list[Job]]:
    grouped: dict[str, list[Job]] = defaultdict(list)
    for job in jobs:
        grouped[job.company].append(job)
    return grouped


if __name__ == "__main__":
    raise SystemExit(run())
