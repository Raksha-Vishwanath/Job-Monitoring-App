from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Jane Street",
        start_url="https://job-boards.greenhouse.io/janestreet",
        job_href_patterns=[r"/janestreet/jobs/"],
    )
