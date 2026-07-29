from __future__ import annotations

import json

from job_monitor.collectors.accenture import AccentureCollector


class _FakeResponse:
    def __init__(self, text: str, url: str = "https://www.accenture.com/us-en/careers/jobsearch") -> None:
        self.text = text
        self.url = url
        self.status_code = 200
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self) -> None:
        return None


class _FakeSession:
    def __init__(self, html: str, payloads: list[dict[str, object]]) -> None:
        self._html = html
        self._payloads = payloads
        self.get_calls: list[tuple[str, dict[str, str] | None]] = []
        self.post_calls: list[dict[str, object]] = []
        self.cookies = {}

    def get(self, url: str, timeout: float, headers: dict[str, str] | None = None) -> _FakeResponse:
        self.get_calls.append((url, headers))
        return _FakeResponse(self._html, url)

    def post(
        self,
        url: str,
        *,
        files: list[tuple[str, tuple[None, str]]],
        headers: dict[str, str],
        timeout: float,
    ) -> _FakeResponse:
        payload = {key: value for key, (_, value) in files}
        self.post_calls.append({"url": url, "payload": payload, "headers": headers})
        index = len(self.post_calls) - 1
        return _FakeResponse(json.dumps(self._payloads[index]))


def test_accenture_payload_matches_bundle_shape(monkeypatch) -> None:
    collector = AccentureCollector()
    monkeypatch.setattr(
        collector,
        "_load_search_config",
        lambda: {
            "jobCountry": "USA",
            "jobLanguage": "en",
            "countrySite": "us-en",
            "minScore": "0.6",
        },
    )

    payloads = collector._payload_variants()

    assert payloads[0]["sortBy"] == "2"
    assert "sortByLabelMapping" not in payloads[0]
    assert payloads[0]["startIndex"] == "0"
    assert payloads[0]["maxResultSize"] == "12"
    assert payloads[0]["countrySite"] == "us-en"
    assert payloads[0]["minScore"] == "0.6"


def test_accenture_fetch_jobs_parses_api_response(monkeypatch) -> None:
    html = """
    <div class="rad-job-search__filters-and-cards"
         data-countrycode="USA"
         data-language-code="en"
         data-countryselector="us-en"
         data-minscore="0.6"></div>
    """
    payload = {
        "data": [
            {
                "title": "Senior Engineer",
                "jobDetailUrl": "/us-en/careers/jobdetails?id=ABC_en&title=Senior+Engineer",
                "location": "Austin, TX",
                "requisitionId": "ABC_en",
            }
        ],
        "totalHits": {"total": 1},
    }
    collector = AccentureCollector()
    collector._session = _FakeSession(html, [payload])  # type: ignore[assignment]
    monkeypatch.setattr(collector, "_fetch_csrf_token", lambda: "token")

    jobs = collector.fetch_jobs()

    assert len(jobs) == 1
    assert jobs[0].company == "Accenture"
    assert jobs[0].job_id == "ABC_en"
    assert jobs[0].title == "Senior Engineer"
    assert jobs[0].location == "Austin, TX"
    assert jobs[0].url.endswith("id=ABC_en&title=Senior+Engineer")
