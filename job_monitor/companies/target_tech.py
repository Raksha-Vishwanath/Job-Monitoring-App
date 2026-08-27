from job_monitor.collectors.workday import WorkdayCollector


def collector() -> WorkdayCollector:
    return WorkdayCollector(
        company="Target Tech",
        base_url="https://target.wd5.myworkdayjobs.com",
        tenant="target",
        site="targetcareers",
    )

