from job_monitor.collectors.phenom import PhenomCollector


def collector() -> PhenomCollector:
    return PhenomCollector(
        company="Snowflake",
        page_url="https://careers.snowflake.com/us/en/search-results",
    )
