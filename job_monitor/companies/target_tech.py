from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Target Tech",
        start_url="https://jobs.target.com/",
        job_href_patterns=[r"/job/", r"/jobs?/"],
    )

