from job_monitor.collectors.lever import LeverCollector


def collector() -> LeverCollector:
    return LeverCollector(company="Palantir Technologies", board_slug="palantir")
