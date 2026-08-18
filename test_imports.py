import importlib
import sys

mods = [
    'job_monitor.companies.registry',
]
errs = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        errs.append((m, e))

if errs:
    print('IMPORT ERRORS:')
    for m, e in errs:
        print(f"{m}: {e}")
    sys.exit(1)

from job_monitor.companies.registry import build_collectors
collectors = build_collectors()
print('collectors count:', len(collectors))
print('collector classes:', [c.__class__.__name__ for c in collectors])
print('OK')
