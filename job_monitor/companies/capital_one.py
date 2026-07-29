from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Capital One",
        start_url="https://www.capitalonecareers.com/search-jobs",
        job_href_patterns=[r"/job/", r"/jobs?/"],
    )

