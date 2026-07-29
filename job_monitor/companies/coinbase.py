from job_monitor.collectors.greenhouse import GreenhouseCollector


def collector() -> GreenhouseCollector:
    return GreenhouseCollector(company="Coinbase", board_slug="coinbase")
