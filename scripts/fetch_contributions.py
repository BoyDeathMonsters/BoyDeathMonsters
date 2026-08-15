#!/usr/bin/env python3
"""
Fetch GitHub contributions SVG for a user and save parsed data.
Requires: requests, beautifulsoup4
"""
import json
import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = "BoyDeathMonsters"
OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

url = f"https://github.com/users/{USERNAME}/contributions"
headers = {"User-Agent": "github-contrib-fetcher/1.0"}
print(f"Fetching contributions for {USERNAME} from {url}")
resp = requests.get(url, headers=headers, timeout=15)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")
svg = soup.find("svg", attrs={"class": "js-calendar-graph-svg"}) or soup.find("svg")
if svg is None:
    print("Could not find contributions SVG on the page", file=sys.stderr)
    sys.exit(2)

# save raw svg
raw_path = os.path.join(OUT_DIR, "contributions_raw.svg")
with open(raw_path, "w", encoding="utf-8") as f:
    f.write(str(svg))
print(f"Saved raw contributions SVG to {raw_path}")

# parse rects with data-date and data-count
rects = svg.find_all("rect")
data = []
for r in rects:
    date = r.get("data-date")
    count = r.get("data-count")
    fill = r.get("fill") or r.get("data-fill")
    if date and count is not None:
        try:
            count_i = int(count)
        except Exception:
            try:
                count_i = int(r.get("aria-label", "0").split()[0])
            except Exception:
                count_i = 0
        data.append({"date": date, "count": count_i, "fill": fill})

out_json = os.path.join(OUT_DIR, "contributions.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump({"username": USERNAME, "fetched_at": datetime.utcnow().isoformat() + "Z", "data": data}, f, indent=2)

print(f"Parsed {len(data)} day entries and wrote to {out_json}")
