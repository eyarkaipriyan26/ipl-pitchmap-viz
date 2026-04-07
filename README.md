# IPL Pitchmap Viz

This repository now includes a working **pitchmap visualization output** from ball-by-ball commentary text.

## Current workflow

1. Load IPL series schedule URLs and extract series IDs.
2. Build/collect commentary rows (`ipl_year, match_id, over_ball, bowler, batter, commentary`).
3. Map commentary text to a **6 x 5 pitch grid** using line/length phrase matching.
4. Render a confidence-weighted pitchmap as a standalone HTML file.

## Structure

- `data/ipl_series_urls.csv`: IPL season schedule URLs (2008-2026).
- `data/sample_commentary.csv`: sample commentary input for visualization testing.
- `src/ipl_pitchmap/url_pipeline.py`: series/match ID parsing.
- `src/ipl_pitchmap/pitch_mapper.py`: line + length extraction and confidence scoring.
- `src/ipl_pitchmap/pitchmap_viz.py`: grid aggregation and HTML/SVG visualization renderer.
- `src/ipl_pitchmap/cli.py`: command line interface.

## Commands

```bash
python -m src.ipl_pitchmap.cli series --csv data/ipl_series_urls.csv
python -m src.ipl_pitchmap.cli build-pitchmap --input-csv data/sample_commentary.csv --output-html artifacts/pitchmap.html
```

Then open `artifacts/pitchmap.html` in your browser.

## Notes

- This design intentionally uses commentary text (publicly available) instead of unavailable ball-tracking coordinates.
- If only line or length is detected, that ball still contributes with lower confidence.
- You can later enrich rows with batter hand (`RHB/LHB`) and bowler arm for split visuals.


## GitHub Pages

To publish quickly, copy `artifacts/pitchmap.html` to `docs/index.html` and enable Pages from the `/docs` folder.
