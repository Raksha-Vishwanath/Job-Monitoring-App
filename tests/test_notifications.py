from job_monitor.models.job import Job
from job_monitor.notifications.render import render_new_jobs_email


def test_render_new_jobs_email_groups_by_company():
    jobs = [
        Job(company="Datadog", job_id="1", title="Software Engineer", location="Boston", url="https://example.com/dd"),
        Job(company="Cloudflare", job_id="2", title="Backend Engineer", location="Austin", url="https://example.com/cf"),
    ]

    subject, body = render_new_jobs_email(jobs)

    assert subject == "New jobs found: 2"
    assert "## Cloudflare" in body
    assert "## Datadog" in body
    assert "Location: Boston" in body
    assert "Location: Austin" in body
    assert "URL: https://example.com/dd" in body

