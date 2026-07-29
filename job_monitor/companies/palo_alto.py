from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Palo Alto Networks",
        start_url="https://jobs.paloaltonetworks.com/en/search-jobs",
        job_href_patterns=[r"/job/"],
    )

