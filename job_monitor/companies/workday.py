from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Workday",
        start_url="https://workday.wd5.myworkdayjobs.com/en-US/Workday",
        job_href_patterns=[r"/en-US/Workday/job/"],
    )
