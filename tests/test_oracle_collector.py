from job_monitor.collectors.oracle import OracleCollector


def test_oracle_collector_parses_requisition_payload():
    collector = OracleCollector(
        company="J.P. Morgan Chase & Co.",
        site_number="CX_1001",
        api_base_url="https://jpmc.fa.oraclecloud.com",
        job_base_url="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001",
    )
    payload = {
        "items": [
            {
                "TotalJobsCount": 1,
                "requisitionList": [
                    {
                        "Id": "210577366",
                        "Title": "U.S. Private Bank - Client Service Associate",
                        "PostedDate": "2026-07-15",
                        "PrimaryLocation": "Newark, DE, United States",
                        "workLocation": [
                            {
                                "TownOrCity": "Newark",
                                "Region2": "DE",
                                "Country": "US",
                            }
                        ],
                    }
                ],
            }
        ]
    }

    jobs = collector._parse_payload(payload)

    assert len(jobs) == 1
    assert jobs[0].company == "J.P. Morgan Chase & Co."
    assert jobs[0].job_id == "210577366"
    assert jobs[0].title == "U.S. Private Bank - Client Service Associate"
    assert jobs[0].location == "Newark, DE, United States"
    assert jobs[0].url == "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/210577366"
