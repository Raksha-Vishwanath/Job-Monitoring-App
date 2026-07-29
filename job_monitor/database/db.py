from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from job_monitor.models.job import Job


class JobDatabase:
    def __init__(self, db_path: str | Path):
        self._is_memory = str(db_path) == ":memory:"
        self.db_path = Path(db_path) if not self._is_memory else Path(":memory:")
        if not self._is_memory:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(":memory:" if self._is_memory else self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._initialize()

    def close(self) -> None:
        self._conn.close()

    def _initialize(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '',
                url TEXT NOT NULL,
                date_posted TEXT,
                first_seen_timestamp TEXT NOT NULL
            )
            """
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
        self._conn.commit()

    def existing_job_ids(self, job_ids: Iterable[str]) -> set[str]:
        ids = [job_id for job_id in job_ids]
        if not ids:
            return set()
        placeholders = ",".join("?" for _ in ids)
        query = f"SELECT job_id FROM jobs WHERE job_id IN ({placeholders})"
        rows = self._conn.execute(query, ids).fetchall()
        return {row["job_id"] for row in rows}

    def insert_jobs(self, jobs: Iterable[Job]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        payload = [
            (
                job.job_id,
                job.company,
                job.title,
                job.location,
                job.url,
                job.date_posted.isoformat() if job.date_posted else None,
                now,
            )
            for job in jobs
        ]
        if not payload:
            return 0
        before = self._conn.total_changes
        self._conn.executemany(
            """
            INSERT OR IGNORE INTO jobs (
                job_id, company, title, location, url, date_posted, first_seen_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        self._conn.commit()
        return self._conn.total_changes - before

    def list_all_jobs(self) -> list[sqlite3.Row]:
        rows = self._conn.execute(
            "SELECT job_id, company, title, location, url, date_posted, first_seen_timestamp FROM jobs ORDER BY company, title"
        ).fetchall()
        return list(rows)
