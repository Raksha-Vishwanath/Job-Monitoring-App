from job_monitor.collectors.oracle import OracleCollector


def collector() -> OracleCollector:
    return OracleCollector(
        company="Akamai Technologies",
        site_number="CX_1",
        api_base_url="https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com",
        job_base_url="https://jobs.akamai.com/en/sites/CX_1",
        location_id="300000000469666",
    )

