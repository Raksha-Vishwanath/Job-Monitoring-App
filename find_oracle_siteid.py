import urllib.request
import json

print("=== Finding correct Oracle site number and location ID ===")

# The API base URL appears to be correct: https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com
# But we need the right siteNumber
# Common site numbers could be: 1, 2, CX_1, CX_2, ORACLE_CAREERS, etc.

api_base = "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com"
site_numbers = ["1", "2", "CX_1", "ORACLE_CAREERS", "ORACLE", "ORG", "ORG_1"]
location_ids = ["300000000149325", None]  # Given location ID and try without it

for site_num in site_numbers:
    for loc_id in location_ids:
        url = (
            f"{api_base}/hcmRestApi/resources/latest/recruitingCEJobRequisitions"
            f"?onlyData=true&expand=requisitionList.secondaryLocations,requisitionList.workLocation"
            f"&finder=findReqs;siteNumber={site_num}"
        )
        if loc_id:
            url += f",locationId={loc_id}"
        url += ",limit=10,offset=0"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get('items', [])
                if len(items) > 0:
                    print(f"✓ FOUND: siteNumber={site_num}, locationId={loc_id}")
                    print(f"  URL: {url[:100]}...")
                    print(f"  Jobs returned: {len(items)}")
                    print(f"  Sample: {items[0].get('title', 'N/A')}")
                    break
        except:
            pass
    else:
        continue
    break

# If nothing found above, try to list all available sites
print("\n=== Trying to list all site numbers ===")
try:
    url = f"{api_base}/hcmRestApi/resources/latest/recruitingCESites?onlyData=true"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        sites = data.get('items', [])
        print(f"Available sites: {len(sites)}")
        for site in sites[:5]:
            print(f"  {site.get('siteNumber', 'N/A')} - {site.get('siteName', 'N/A')}")
except Exception as e:
    print(f"Could not list sites: {str(e)[:80]}")
