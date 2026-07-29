from job_monitor.collectors.greenhouse import GreenhouseCollector


def collector() -> GreenhouseCollector:
    return GreenhouseCollector(company="LinkedIn", board_slug="linkedin")
