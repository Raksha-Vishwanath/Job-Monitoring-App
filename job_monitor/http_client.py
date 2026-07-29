from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Mapping

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(frozen=True)
class HttpResponse:
    url: str
    status_code: int
    text: str
    headers: Mapping[str, str]


def build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "POST"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": "job-monitor/1.0 (+https://github.com/)",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        }
    )
    return session


def get_with_timeout(
    session: requests.Session,
    url: str,
    *,
    timeout: float = 20.0,
    headers: Mapping[str, str] | None = None,
) -> HttpResponse:
    response = session.get(url, timeout=timeout, headers=headers)
    if response.status_code == 429:
        # A small jitter helps avoid hammering rate-limited endpoints during retries.
        time.sleep(1.5 + random.random())
    response.raise_for_status()
    return HttpResponse(
        url=response.url,
        status_code=response.status_code,
        text=response.text,
        headers=response.headers,
    )
