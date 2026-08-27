from job_monitor.collectors.workday import WorkdayCollector


def collector() -> WorkdayCollector:
    return WorkdayCollector(
        company="Workday",
        base_url="https://workday.wd5.myworkdayjobs.com",
        tenant="workday",
        site="Workday",
    )
