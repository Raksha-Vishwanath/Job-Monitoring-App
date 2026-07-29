from __future__ import annotations

from hashlib import sha256


def stable_job_hash(company: str, title: str, location: str, url: str) -> str:
    """Return a stable canonical identifier for jobs that do not expose an id."""

    payload = "\u241f".join(
        [
            company.strip().lower(),
            title.strip().lower(),
            location.strip().lower(),
            url.strip().lower(),
        ]
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def normalize_company_slug(company: str) -> str:
    slug = company.strip().lower()
    out = []
    last_hyphen = False
    for char in slug:
        if char.isalnum():
            out.append(char)
            last_hyphen = False
        elif not last_hyphen:
            out.append("-")
            last_hyphen = True
    return "".join(out).strip("-")

