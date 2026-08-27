from job_monitor.collectors.amazon import AmazonJobsCollector


def collector() -> AmazonJobsCollector:
    return AmazonJobsCollector(
        company="AWS",
        search_url="https://www.amazon.jobs/en/search?base_query=&loc_query=united+states&type=area&longitude=-77.03196&latitude=38.89036&country=USA",
    )
