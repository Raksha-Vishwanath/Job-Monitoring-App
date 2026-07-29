from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="CrowdStrike",
        start_url="https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers",
        job_href_patterns=[r"/job/"],
    )

