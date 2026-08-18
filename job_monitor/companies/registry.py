from __future__ import annotations

from collections.abc import Iterable

from job_monitor.collectors.base import JobCollector
from job_monitor.companies.accenture import collector as accenture_collector
from job_monitor.companies.airbnb import collector as airbnb_collector
from job_monitor.companies.anthropic import collector as anthropic_collector
from job_monitor.companies.akamai import collector as akamai_collector
from job_monitor.companies.coinbase import collector as coinbase_collector
from job_monitor.companies.cloudflare import collector as cloudflare_collector
from job_monitor.companies.crowdstrike import collector as crowdstrike_collector
from job_monitor.companies.databricks import collector as databricks_collector
from job_monitor.companies.datadog import collector as datadog_collector
from job_monitor.companies.hinge_health import collector as hinge_health_collector
from job_monitor.companies.jpmorgan import collector as jpmorgan_collector
from job_monitor.companies.openai import collector as openai_collector
from job_monitor.companies.palantir_technologies import collector as palantir_technologies_collector
from job_monitor.companies.robinhood import collector as robinhood_collector
from job_monitor.companies.target_tech import collector as target_tech_collector
from job_monitor.companies.workday import collector as workday_collector
from job_monitor.companies.walmart_global_tech import collector as walmart_global_tech_collector
from job_monitor.companies.wayfair import collector as wayfair_collector
from job_monitor.companies.zscaler import collector as zscaler_collector


def build_collectors() -> list[JobCollector]:
    # Active monitored collectors. Removed companies: LinkedIn, Stripe,
    # Palo Alto Networks, ServiceNow, Capital One, Fidelity, Expedia Group, Snowflake
    return [
        datadog_collector(),
        cloudflare_collector(),
        crowdstrike_collector(),
        zscaler_collector(),
        jpmorgan_collector(),
        databricks_collector(),
        accenture_collector(),
        hinge_health_collector(),
        robinhood_collector(),
        coinbase_collector(),
        airbnb_collector(),
        openai_collector(),
        palantir_technologies_collector(),
        wayfair_collector(),
        walmart_global_tech_collector(),
        target_tech_collector(),
        akamai_collector(),
        workday_collector(),
        anthropic_collector(),
    ]
