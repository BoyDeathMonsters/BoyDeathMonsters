#!/usr/bin/env python3
"""
Render a simple demo SVG (and info-card.svg) from the raw contributions SVG saved by fetch_contributions.py
If an avi-ascii.svg file exists at the repository root, inline it into the generated SVGs.
"""
import json
import os
from datetime import datetime

HERE = os.path.dirname(__file__)
REPO_ROOT = os.path.normpath(os.path.join(HERE, '..'))
DATA_DIR = os.path.join(HERE, "data")
RAW_SVG = os.path.join(DATA_DIR, "contributions_raw.svg")
OUT_DEMO = os.path.join(REPO_ROOT, "demo.svg")
OUT_INFO = os.path.join(REPO_ROOT, "info-card.svg")
AVI_SVG_PATH = os.path.join(REPO_ROOT, "avi-ascii.svg")

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

# Load avi-ascii.svg if present
avi_inner = None
if os.path.exists(AVI_SVG_PATH):
    try:
        avi_raw = open(AVI_SVG_PATH, 'r', encoding='utf-8').read()
        # Strip xml declaration if present
        avi_inner = avi_raw
        if avi_inner.lstrip().startswith("<?xml"):
            avi_inner = avi_inner[avi_inner.find('?>')+2:]
        # If it contains an outer <svg>, keep the whole svg block so it can be positioned with a group
        # We'll wrap it later in a <g> with a transform to position/scale it
    except Exception:
        avi_inner = None

# Build demo svg: wrap the contributions graphic with a small title
width = 900
height = 240
now = datetime.utcnow().strftime('%Y-%m-%d')

# If avi is present, reserve some space on the right and scale it down
avi_group = ''
if avi_inner:
    # Position avi at top-right of the demo card
    # We'll place it at x=700,y=8 and scale to fit (user's avi svg should be reasonably sized)
    avi_group = f"\n    <g transform=\"translate(700,8) scale(0.5)\">\n{avi_inner}\n    </g>\n"

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
{avi_group}
</svg>
'''

with open(OUT_DEMO, "w", encoding="utf-8") as f:
    f.write(demo_svg)
print(f"Wrote demo SVG to {OUT_DEMO}")

# Create a simple info-card that includes the demo svg inline (small card)
info_width = 640
info_height = 200

# Prepare avi insertion for info card (placed on the right side inside the white panel)
info_avi_group = ''
if avi_inner:
    # scale down more for the smaller card
    info_avi_group = f"\n    <g transform=\"translate(520,16) scale(0.32)\">\n{avi_inner}\n    </g>\n"

info_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{info_width}" height="{info_height}" viewBox="0 0 {info_width} {info_height}">
  <rect width="100%" height="100%" fill="#0b1220" rx="12" />
  <g transform="translate(16,16)">
    <rect width="608" height="168" fill="#ffffff" rx="8" />
    <g transform="translate(8,8)">
{inner}
    </g>
  </g>
{info_avi_group}
</svg>
'''
with open(OUT_INFO, "w", encoding="utf-8") as f:
    f.write(info_svg)
print(f"Wrote info-card SVG to {OUT_INFO}")
''