from job_monitor.collectors.html_board import HtmlBoardCollector


def collector() -> HtmlBoardCollector:
    return HtmlBoardCollector(
        company="Stripe",
        start_url="https://stripe.com/jobs/search",
        job_href_patterns=[r"/jobs?/search", r"/job/", r"/jobs?/"],
    )

