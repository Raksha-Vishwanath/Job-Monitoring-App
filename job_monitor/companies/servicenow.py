from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="ServiceNow",
        start_url="https://careers.servicenow.com/jobs/",
        job_href_patterns=[r"/jobs?/"],
    )

