from job_monitor.main import canonicalize_jobs
from job_monitor.models.job import Job


def test_canonicalize_jobs_removes_duplicate_ids():
    jobs = [
        Job(company="Datadog", job_id="1", title="Engineer", location="Boston", url="https://example.com/a"),
        Job(company="Datadog", job_id="1", title="Engineer Duplicate", location="Austin", url="https://example.com/b"),
    ]

    deduped = canonicalize_jobs(jobs)

    assert len(deduped) == 1
    assert deduped[0].job_id == "1"
    assert deduped[0].title == "Engineer"

