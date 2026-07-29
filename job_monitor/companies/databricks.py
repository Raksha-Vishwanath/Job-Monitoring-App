from job_monitor.collectors.greenhouse import GreenhouseCollector


def collector() -> GreenhouseCollector:
    return GreenhouseCollector(company="Databricks", board_slug="databricks")
