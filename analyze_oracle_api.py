import urllib.request
import re
import json

print("=== Analyzing Oracle Careers API ===")
url = "https://careers.oracle.com/en/sites/jobsearch/jobs?location=United%20States&locationId=300000000149325"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as response:
        content = response.read().decode('utf-8', errors='ignore')
    
    # Look for API calls in the JavaScript
    # Check for references to HCM API or other endpoints
    api_patterns = re.findall(r'(https://[^"\s<>]*(?:hcm|rest|api)[^"\s<>]*)', content, re.IGNORECASE)
    if api_patterns:
        print("Found API endpoints:")
        for api in set(api_patterns)[:10]:
            print(f"  {api}")
    
    # Look for site number or configuration
    site_patterns = re.findall(r'siteNumber["\':=]+["\']?([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
    if site_patterns:
        print(f"\nFound site numbers: {set(site_patterns)}")
    
    # Look for Oracle Cloud domain patterns
    cloud_patterns = re.findall(r'https://[a-z0-9-]+\.fa[^/]+\.ocs\.oraclecloud\.com', content)
    if cloud_patterns:
        print(f"\nFound Oracle Cloud API domains:")
        for domain in set(cloud_patterns):
            print(f"  {domain}")
    
    # Look for any configuration variables
    config_vars = re.findall(r'(?:window|config)\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*["\']?([a-zA-Z0-9_/-]+)["\']?', content)
    if config_vars:
        print(f"\nFound configuration variables:")
        for key, value in config_vars[:10]:
            print(f"  {key} = {value}")
    
except Exception as e:
    print(f"ERROR: {e}")

# Try to find the correct API by checking common patterns
print("\n=== Testing common Oracle HCM API patterns ===")

test_urls = [
    "https://careers.oracle.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=2",
    "https://careers.oracle.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=CX_1",
    "https://fa-extu-saasfaprod1.fa.ocs.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=2",
]

for test_url in test_urls:
    try:
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('items', [])
            print(f"✓ {test_url[:80]}... | {len(items)} jobs")
            break
    except Exception as e:
        print(f"✗ {test_url[:80]}... | {str(e)[:40]}")
