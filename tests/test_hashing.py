from job_monitor.utils import stable_job_hash


def test_stable_job_hash_is_deterministic():
    first = stable_job_hash("Datadog", "Engineer", "Boston", "https://example.com/job/1")
    second = stable_job_hash("Datadog", "Engineer", "Boston", "https://example.com/job/1")
    assert first == second


def test_stable_job_hash_changes_when_input_changes():
    first = stable_job_hash("Datadog", "Engineer", "Boston", "https://example.com/job/1")
    second = stable_job_hash("Datadog", "Engineer", "Austin", "https://example.com/job/1")
    assert first != second

