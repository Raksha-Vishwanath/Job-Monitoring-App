from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Fidelity Investments",
        start_url="https://jobs.fidelity.com/en/jobs/",
        job_href_patterns=[r"/job/", r"/jobs?/"],
    )

