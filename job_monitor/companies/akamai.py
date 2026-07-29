from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Akamai Technologies",
        start_url="https://www.akamai.com/careers",
        job_href_patterns=[r"jobs\.akamai\.com", r"/job/", r"/jobs?/"],
    )

