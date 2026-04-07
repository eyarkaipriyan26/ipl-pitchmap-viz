# IPL Pitchmap Viz (Starter)

This repository now contains a starter pipeline for your phased approach:

1. Load IPL series schedule URLs and extract series IDs.
2. (Next step) fetch each match URL/ID for each season.
3. (Next step) scrape ball-by-ball commentary.
4. Map commentary text to a **6 x 5 pitch grid** with confidence scoring.

## Structure

- `data/ipl_series_urls.csv`: Seed list of IPL schedule URLs (2008-2026).
- `src/ipl_pitchmap/url_pipeline.py`: URL parsing for series and match IDs.
- `src/ipl_pitchmap/pitch_mapper.py`: Rules to infer line/length buckets + confidence.
- `src/ipl_pitchmap/models.py`: Core dataclasses.
- `src/ipl_pitchmap/cli.py`: Small CLI entrypoint.

## Run

```bash
python -m src.ipl_pitchmap.cli series --csv data/ipl_series_urls.csv
```

## Notes

- The mapper is intentionally heuristic because true ball-tracking coordinates are not public for all matches.
- Missing line or length is handled by `UNKNOWN_*` with lower confidence.
- Batter hand and bowler arm can be injected later to adjust sections.
