from job_monitor.collectors.greenhouse import GreenhouseCollector


def test_greenhouse_collector_parses_api_payload():
    collector = GreenhouseCollector(company="Datadog", board_slug="datadog")
    payload = {
        "jobs": [
            {
                "id": 123,
                "title": "Software Engineer",
                "absolute_url": "https://boards.greenhouse.io/datadog/jobs/123",
                "location": {"name": "Boston"},
                "updated_at": "2026-06-21T12:34:56Z",
            }
        ],
        "meta": {"total": 1},
    }

    jobs = collector._parse_payload(payload)

    assert len(jobs) == 1
    assert jobs[0].company == "Datadog"
    assert jobs[0].job_id == "123"
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].location == "Boston"
    assert jobs[0].url == "https://boards.greenhouse.io/datadog/jobs/123"
