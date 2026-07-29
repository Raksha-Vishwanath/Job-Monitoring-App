from job_monitor.collectors.ashby import AshbyCollector


def collector() -> AshbyCollector:
    return AshbyCollector(company="OpenAI", board_slug="openai")
