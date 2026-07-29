from __future__ import annotations

import smtplib
from types import SimpleNamespace

from job_monitor.models.job import Job
from job_monitor.main import run


def test_run_returns_nonzero_when_smtp_auth_fails(monkeypatch):
    config = SimpleNamespace(
        db_path=":memory:",
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user@example.com",
        smtp_password="invalid-password",
        email_from="from@example.com",
        email_to="to@example.com",
    )

    class DummyCollector:
        company = "TestCo"

        def fetch_jobs(self):
            return [
                Job(
                    company="TestCo",
                    job_id="1",
                    title="Software Engineer",
                    location="Remote",
                    url="https://example.com/jobs/1",
                )
            ]

    class DummyDB:
        def __init__(self, db_path):
            self.closed = False

        def existing_job_ids(self, job_ids):
            return set()

        def insert_jobs(self, jobs):
            return len(jobs)

        def close(self):
            self.closed = True

    class FailingSender:
        def __init__(self, host, port, username, password, email_from, email_to):
            pass

        def send(self, subject, body):
            raise smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")

    monkeypatch.setattr("job_monitor.main.load_config", lambda: config)
    monkeypatch.setattr("job_monitor.main.JobDatabase", DummyDB)
    monkeypatch.setattr("job_monitor.main.build_collectors", lambda: [DummyCollector()])
    monkeypatch.setattr("job_monitor.main.render_new_jobs_email", lambda jobs: ("New jobs found: 1", "body"))
    monkeypatch.setattr("job_monitor.main.EmailNotificationSender", FailingSender)

    assert run() == 1
