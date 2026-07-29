from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Walmart Global Tech",
        start_url="https://careers.walmart.com/us/en/results?searchQuery=",
        job_href_patterns=[r"/results", r"/job/", r"/jobs?/"],
    )
