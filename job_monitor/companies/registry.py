from __future__ import annotations

from collections.abc import Iterable

from job_monitor.collectors.base import JobCollector

from job_monitor.companies.accenture import collector as accenture_collector
from job_monitor.companies.airbnb import collector as airbnb_collector
from job_monitor.companies.anthropic import collector as anthropic_collector
from job_monitor.companies.akamai import collector as akamai_collector
from job_monitor.companies.capital_one import collector as capital_one_collector
from job_monitor.companies.coinbase import collector as coinbase_collector
from job_monitor.companies.cloudflare import collector as cloudflare_collector
from job_monitor.companies.crowdstrike import collector as crowdstrike_collector
from job_monitor.companies.databricks import collector as databricks_collector
from job_monitor.companies.datadog import collector as datadog_collector
from job_monitor.companies.expedia_group import collector as expedia_group_collector
from job_monitor.companies.fidelity import collector as fidelity_collector
from job_monitor.companies.hinge_health import collector as hinge_health_collector
from job_monitor.companies.jane_street import collector as jane_street_collector
from job_monitor.companies.jpmorgan import collector as jpmorgan_collector
from job_monitor.companies.linkedin import collector as linkedin_collector
from job_monitor.companies.palo_alto import collector as palo_alto_collector
from job_monitor.companies.openai import collector as openai_collector
from job_monitor.companies.palantir_technologies import collector as palantir_technologies_collector
from job_monitor.companies.robinhood import collector as robinhood_collector
from job_monitor.companies.servicenow import collector as servicenow_collector
from job_monitor.companies.snowflake import collector as snowflake_collector
from job_monitor.companies.splunk import collector as splunk_collector
from job_monitor.companies.stripe import collector as stripe_collector
from job_monitor.companies.target_tech import collector as target_tech_collector
from job_monitor.companies.workday import collector as workday_collector
from job_monitor.companies.walmart_global_tech import collector as walmart_global_tech_collector
from job_monitor.companies.wayfair import collector as wayfair_collector
from job_monitor.companies.zscaler import collector as zscaler_collector


def build_collectors() -> list[JobCollector]:
    return [
        palo_alto_collector(),
        crowdstrike_collector(),
        datadog_collector(),
        cloudflare_collector(),
        zscaler_collector(),
        servicenow_collector(),
        capital_one_collector(),
        jpmorgan_collector(),
        fidelity_collector(),
        akamai_collector(),
        splunk_collector(),
        walmart_global_tech_collector(),
        target_tech_collector(),
        expedia_group_collector(),
        snowflake_collector(),
        stripe_collector(),
        wayfair_collector(),
        accenture_collector(),
        hinge_health_collector(),
        linkedin_collector(),
        robinhood_collector(),
        coinbase_collector(),
        databricks_collector(),
        airbnb_collector(),
        jane_street_collector(),
        openai_collector(),
        anthropic_collector(),
        palantir_technologies_collector(),
        workday_collector(),
    ]
