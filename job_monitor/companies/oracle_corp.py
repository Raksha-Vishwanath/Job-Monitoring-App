from job_monitor.collectors.oracle import OracleCollector


def collector():
    """Oracle HCM API collector for US positions"""
    return OracleCollector(
        company="Oracle",
        site_number="1",
        api_base_url="https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com",
        job_base_url="https://careers.oracle.com/en/sites/jobsearch/details/",
        location_id="300000000149325",  # United States
    )
