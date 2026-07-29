from job_monitor.database.db import JobDatabase
from job_monitor.models.job import Job


def test_database_inserts_jobs_and_ignores_duplicates():
    db = JobDatabase(":memory:")
    job = Job(company="Datadog", job_id="abc", title="Engineer", location="Boston", url="https://example.com/a")

    first_insert = db.insert_jobs([job])
    second_insert = db.insert_jobs([job])

    rows = db.list_all_jobs()

    assert first_insert == 1
    assert second_insert == 0
    assert len(rows) == 1
    assert rows[0]["job_id"] == "abc"
    assert rows[0]["company"] == "Datadog"
