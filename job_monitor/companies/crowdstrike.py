from job_monitor.collectors.workday import WorkdayCollector


def collector() -> WorkdayCollector:
    return WorkdayCollector(
        company="CrowdStrike",
        base_url="https://crowdstrike.wd5.myworkdayjobs.com",
        tenant="crowdstrike",
        site="crowdstrikecareers",
    )

