from job_monitor.collectors.ashby import AshbyCollector


def collector() -> AshbyCollector:
    return AshbyCollector(company="Anthropic", board_slug="odewithanthropic")
