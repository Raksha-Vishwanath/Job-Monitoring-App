from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Zscaler",
        start_url="https://www.zscaler.com/careers/search",
        job_href_patterns=[r"/jobs?/"],
    )

