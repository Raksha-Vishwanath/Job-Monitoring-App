from job_monitor.collectors.hinge import HingeCollector


def collector() -> HingeCollector:
    return HingeCollector()
