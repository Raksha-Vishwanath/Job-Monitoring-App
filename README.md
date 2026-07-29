# Job Monitor

This repository contains a Python 3.12 job-monitoring app that:

- fetches job postings from a fixed company list
- stores previously seen jobs in SQLite
- detects newly discovered jobs
- sends exactly one email when new jobs are found
- runs automatically from GitHub Actions on a daily schedule

## Architecture

The app is intentionally small and modular:

- `job_monitor/models/job.py` defines the normalized `Job` model with Pydantic.
- `job_monitor/database/db.py` stores seen jobs in SQLite.
- `job_monitor/collectors/` contains reusable collectors.
- `job_monitor/companies/` contains one module per company.
- `job_monitor/notifications/` renders and sends email notifications.
- `job_monitor/main.py` orchestrates the full run.

Collectors implement a shared `fetch_jobs() -> list[Job]` interface so new companies can be added later without changing the rest of the system.

## Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Execution

Run the monitor from the repository root:

```bash
python main.py
```

By default the SQLite database is stored at `data/jobs.sqlite3`.

## Email Configuration

Set these environment variables when you want notifications:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

The app sends a single email per execution only when new jobs are discovered.

## GitHub Actions

The workflow at `.github/workflows/daily_monitor.yml`:

- runs automatically once per day
- can also be triggered manually
- installs dependencies
- runs `main.py`
- commits the updated SQLite database back to the repository when it changes

Add the SMTP values above to GitHub repository secrets before enabling the workflow.

## Notes

- Job IDs are used for deduplication when available.
- If a source does not provide a stable job ID, the app generates one from company, title, location, and URL.
- One company failure does not stop the full run.
- HTTP requests use retries and timeouts.

