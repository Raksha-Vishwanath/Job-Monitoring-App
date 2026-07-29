from job_monitor.collectors.accenture import AccentureCollector


def collector() -> AccentureCollector:
    return AccentureCollector()
