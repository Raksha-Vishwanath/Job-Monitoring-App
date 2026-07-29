from job_monitor.collectors.oracle import OracleCollector


def collector() -> OracleCollector:
    return OracleCollector(
        company="J.P. Morgan Chase & Co.",
        site_number="CX_1001",
        api_base_url="https://jpmc.fa.oraclecloud.com",
        job_base_url="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001",
    )
