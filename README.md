# IPL Pitchmap Viz

This repo now supports the full pipeline:

1. Take IPL season fixture URLs.
2. Crawl match URLs for each season.
3. Scrape ball-by-ball commentary from each match page.
4. Map commentary to a 6x5 pitch grid with confidence.
5. Render RHB/LHB pitchmap visualization as HTML.

## Structure

- `data/ipl_series_urls.csv`: IPL season schedule URLs (2008-2026).
- `data/sample_commentary.csv`: sample commentary input for quick visualization checks.
- `src/ipl_pitchmap/scraper.py`: schedule crawling + commentary scraping.
- `src/ipl_pitchmap/pitch_mapper.py`: line + length extraction and confidence scoring.
- `src/ipl_pitchmap/pitchmap_viz.py`: grid aggregation and HTML/SVG visualization renderer.
- `src/ipl_pitchmap/cli.py`: command line interface.

## Commands

```bash
# Quick check: parse season IDs
python -m src.ipl_pitchmap.cli series --csv data/ipl_series_urls.csv

# Real scrape: all commentary rows (use --years for targeted runs)
python -m src.ipl_pitchmap.cli scrape-full-commentary \
  --series-csv data/ipl_series_urls.csv \
  --output-csv data/ipl_commentary_full.csv \
  --years 2024 2025

# Build pitchmap from scraped CSV
python -m src.ipl_pitchmap.cli build-pitchmap \
  --input-csv data/ipl_commentary_full.csv \
  --output-html artifacts/pitchmap.html
```

## GitHub Pages

- Keep `docs/index.html` as the published entrypoint.
- After regenerating `artifacts/pitchmap.html`, copy it to `docs/index.html` and push.

## Notes

- Commentary schema on source pages can change over time; scraper is defensive and extracts from embedded `__NEXT_DATA__` JSON.
- If a ball has only line or only length text, it is still counted with lower confidence.
