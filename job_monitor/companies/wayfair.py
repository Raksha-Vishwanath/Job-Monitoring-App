from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Wayfair",
        start_url="https://www.wayfair.com/careers/jobs",
        job_href_patterns=[r"/careers/jobs", r"/job/", r"/jobs?/"],
    )
