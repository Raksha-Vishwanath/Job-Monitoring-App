from job_monitor.collectors.greenhouse import GreenhouseCollector


def collector() -> GreenhouseCollector:
    return GreenhouseCollector(company="Cloudflare", board_slug="cloudflare")
