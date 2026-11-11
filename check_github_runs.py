import urllib.request
import json

repo = "pavankumar9d-rgb/AI-Automation"
url = f"https://api.github.com/repos/{repo}/actions/runs"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        runs = data.get("workflow_runs", [])
        print(f"Total workflow runs found: {len(runs)}")
        for r in runs[:5]:
            print(f"Run #{r.get('run_number')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')} | Created: {r.get('created_at')} | Event: {r.get('event')}")
except Exception as err:
    print("Error querying GitHub API:", err)

