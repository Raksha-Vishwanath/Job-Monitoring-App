from job_monitor.collectors.hinge import HingeCollector
from job_monitor.collectors.phenom import PhenomCollector


def test_phenom_collector_extracts_embedded_jobs():
    collector = PhenomCollector(company="Splunk", page_url="https://careers.cisco.com/global/en/splunk/search-page")
    html = """
    <html><script>
    phApp.ddo = {"eagerLoadRefineSearch":{"status":200,"hits":10,"totalHits":1,"data":{"jobs":[{"title":"Solutions Architect","reqId":"2017728","city":"Austin","state":"Texas","applyUrl":"https://example.com/job/1","postedDate":"2026-07-01T00:00:00.000+0000"}]}}};
    </script></html>
    """.strip()

    payload = collector._extract_eager_load_payload(html)
    assert payload is not None
    jobs = payload.get("data", {}).get("jobs", [])
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Solutions Architect"


def test_hinge_collector_extracts_app_data():
    collector = HingeCollector()
    html = """
    <html><script>
    window.__appData = {"jobBoard":{"jobPostings":[{"title":"Data Scientist","jobRequisitionId":"H-1","locationName":"Remote","publishedDate":"2026-07-01T00:00:00.000+0000"}]}};
    </script></html>
    """.strip()

    payload = collector._extract_app_data(html)
    assert payload is not None
    assert payload["jobBoard"]["jobPostings"][0]["title"] == "Data Scientist"
