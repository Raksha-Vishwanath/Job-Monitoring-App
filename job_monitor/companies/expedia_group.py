from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Expedia Group",
        start_url="https://careers.expediagroup.com/jobs/",
        job_href_patterns=[r"/job/", r"/jobs?/"],
    )

