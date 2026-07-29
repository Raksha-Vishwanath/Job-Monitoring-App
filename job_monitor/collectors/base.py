from __future__ import annotations

from abc import ABC, abstractmethod

from job_monitor.models.job import Job


class JobCollector(ABC):
    @abstractmethod
    def fetch_jobs(self) -> list[Job]:
        raise NotImplementedError

