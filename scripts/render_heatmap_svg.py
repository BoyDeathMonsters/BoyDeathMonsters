#!/usr/bin/env python3
"""
Render a simple demo SVG (and info-card.svg) from the raw contributions SVG saved by fetch_contributions.py
"""
import json
import os
from datetime import datetime

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")
RAW_SVG = os.path.join(DATA_DIR, "contributions_raw.svg")
OUT_DEMO = os.path.join(os.path.dirname(HERE), "demo.svg")
OUT_INFO = os.path.join(os.path.dirname(HERE), "info-card.svg")

if not os.path.exists(RAW_SVG):
    raise SystemExit("Raw contributions SVG not found. Run scripts/fetch_contributions.py first.")

raw = open(RAW_SVG, "r", encoding="utf-8").read()

# Try to extract inner svg content (strip <?xml ...?> and outer <svg> tags if present)
inner = raw
# Remove xml declaration if present
if inner.lstrip().startswith("<?xml"):
    inner = inner[inner.find('?>')+2:]
# Remove outer <svg ...> and </svg>
if "<svg" in inner:
    first = inner.find('<svg')
    start = inner.find('>', first) + 1
    end = inner.rfind('</svg>')
    if start > 0 and end > start:
        inner = inner[start:end]

# Build demo svg: wrap the contributions graphic with a small title
width = 900
height = 240
now = datetime.utcnow().strftime('%Y-%m-%d')

demo_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .title {{ font: 600 18px/1.2 "Segoe UI", Roboto, "Helvetica Neue", Arial; fill: #0f172a; }}
  </style>
  <rect width="100%" height="100%" fill="#ffffff" rx="8" />
  <text x="20" y="28" class="title">GitHub contributions ({now})</text>
  <g transform="translate(20,40)">
{inner}
  </g>
</svg>
'''

with open(OUT_DEMO, "w", encoding="utf-8") as f:
    f.write(demo_svg)
print(f"Wrote demo SVG to {OUT_DEMO}")

# Create a simple info-card that includes the demo svg inline (small card)
info_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="640" height="200" viewBox="0 0 640 200">
  <rect width="100%" height="100%" fill="#0b1220" rx="12" />
  <g transform="translate(16,16)">
    <rect width="608" height="168" fill="#ffffff" rx="8" />
    <g transform="translate(8,8)">
{inner}
    </g>
  </g>
</svg>
'''
with open(OUT_INFO, "w", encoding="utf-8") as f:
    f.write(info_svg)
print(f"Wrote info-card SVG to {OUT_INFO}")
