from job_monitor.collectors.html_board import HtmlBoardCollector


def test_html_board_collector_skips_cta_links():
    collector = HtmlBoardCollector(
        company="ExampleCo",
        start_url="https://example.com/jobs",
        job_href_patterns=[r"/job/"],
    )

    html = """
    <html>
      <body>
        <section id="results">
          <a href="/job/senior-engineer">Senior Engineer</a>
          <a href="/job/senior-engineer">View Job</a>
          <a href="/product/jobs-monitoring">Jobs Monitoring</a>
        </section>
      </body>
    </html>
    """

    jobs, next_url = collector._parse_page("https://example.com/jobs", html)

    assert next_url is None
    assert len(jobs) == 1
    assert jobs[0].title == "Senior Engineer"
    assert jobs[0].url == "https://example.com/job/senior-engineer"
