from job_monitor.collectors.greenhouse import GreenhouseCollector


def collector() -> GreenhouseCollector:
    return GreenhouseCollector(company="Airbnb", board_slug="airbnb")
