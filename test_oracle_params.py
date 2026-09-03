import urllib.request
import json

print("=== Checking Oracle jobs with different parameters ===")

api_base = "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com"

# Test with and without location ID, and with larger page sizes
tests = [
    ("With locationId=300000000149325, limit=100", "1", "300000000149325", 100),
    ("Without locationId, limit=100", "1", None, 100),
    ("Without locationId, limit=200", "1", None, 200),
]

for desc, site_num, loc_id, limit in tests:
    url = (
        f"{api_base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
        f"?onlyData=true&expand=requisitionList.secondaryLocations,requisitionList.workLocation"
        f"&finder=findReqs;siteNumber={site_num}"
    )
    if loc_id:
        url += f",locationId={loc_id}"
    url += f",limit={limit},offset=0"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('items', [])
            total = data.get('totalResults', len(items))
            print(f"✓ {desc}")
            print(f"  Jobs returned: {len(items)}, Total: {total}")
            if items:
                for job in items[:3]:
                    location = job.get('workLocation', {}).get('countryDesc', 'Unknown')
                    title = job.get('title', 'N/A')
                    print(f"    - {title} ({location})")
    except Exception as e:
        print(f"✗ {desc}: {str(e)[:60]}")
    print()
