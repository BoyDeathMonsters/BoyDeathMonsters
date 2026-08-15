<!-- README snippet: profile art and info card -->

## Profile art (generated)

This repository contains scripts that fetch your GitHub contributions calendar and render a simple SVG heatmap. Run the scripts locally to regenerate the artwork:

- pip install requests beautifulsoup4 --break-system-packages
- python scripts/fetch_contributions.py
- python scripts/render_heatmap_svg.py

The workflow .github/workflows/update_profile_art.yml can also be triggered manually from the Actions tab to regenerate and commit demo.svg and info-card.svg automatically.
