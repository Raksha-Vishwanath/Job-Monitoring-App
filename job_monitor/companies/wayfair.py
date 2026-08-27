from job_monitor.collectors.wayfair import WayfairCollector


def collector() -> WayfairCollector:
    return WayfairCollector(
        company="Wayfair",
        page_url="https://www.wayfair.com/careers/jobs?keywords=&locationIds=&stateIds=&countryIds=1",
    )
