from job_monitor.collectors.phenom import PhenomCollector


def collector() -> PhenomCollector:
    return PhenomCollector(
        company="Splunk",
        page_url="https://careers.cisco.com/global/en/splunk/search-page",
    )
