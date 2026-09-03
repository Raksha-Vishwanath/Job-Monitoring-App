from job_monitor.companies.registry import build_collectors

print("=" * 70)
print("FINAL VALIDATION TEST - Active Collectors")
print("=" * 70)

collectors = build_collectors()
results = {}
errors = []

print("\nFetching jobs from all collectors...\n")

for collector in collectors:
    try:
        jobs = collector.fetch_jobs()
        results[collector.company] = len(jobs)
        status = "✓" if len(jobs) > 0 else "·"
        print(f"{status} {collector.company:25} | {len(jobs):5} jobs")
    except Exception as e:
        results[collector.company] = 0
        errors.append((collector.company, str(e)[:60]))
        print(f"✗ {collector.company:25} | ERROR")

print("\n" + "=" * 70)
print(f"Summary: {len(collectors)} collectors, {sum(1 for v in results.values() if v > 0)} returning jobs")
print(f"Total jobs collected: {sum(results.values())}")
print(f"Errors: {len(errors)}")

if errors:
    print("\nErrors encountered:")
    for company, error in errors:
        print(f"  - {company}: {error}")

print("\n✓ VALIDATION COMPLETE")
print(f"  - Active collectors: {len(collectors)}")
print(f"  - Collectors returning jobs: {sum(1 for v in results.values() if v > 0)}")
print("=" * 70)
