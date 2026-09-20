"""Read-only smoke checks, including a database-backed request via the ALB."""
import json
import time
import urllib.request

BASE = "http://linkedin-alb-976933077.us-west-1.elb.amazonaws.com"

for attempt in range(12):
    try:
        with urllib.request.urlopen(BASE + "/", timeout=10) as response:
            page = response.read().decode()
            if '<div id="root"' not in page:
                raise ValueError("React entry page not found")
        with urllib.request.urlopen(BASE + "/api/feed", timeout=10) as response:
            if not isinstance(json.load(response), list):
                raise ValueError("Expected a JSON feed")
        print("Public frontend and database-backed API checks passed")
        break
    except Exception:
        if attempt == 11:
            raise SystemExit("Public smoke check failed. Inspect ALB targets and use manual rollback if needed.")
        time.sleep(10)
