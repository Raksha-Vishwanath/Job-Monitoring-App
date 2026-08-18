from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Anthropic",
        start_url="https://www.anthropic.com/careers/jobs",
        job_href_patterns=[r"/careers/jobs", r"/jobs/", r"/job/"],
    )
