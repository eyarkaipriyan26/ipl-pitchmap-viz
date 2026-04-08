import argparse
from pathlib import Path

from .pitchmap_viz import render_pitchmap_html
from .scraper import extract_match_urls, fetch_html, scrape_match_commentary, write_commentary_csv
from .url_pipeline import load_series_refs


def cmd_series(args: argparse.Namespace) -> None:
    refs = load_series_refs(args.csv)
    for ref in refs:
        print(f"{ref.year}: series_id={ref.series_id} url={ref.url}")


def cmd_scrape_full_commentary(args: argparse.Namespace) -> None:
    refs = load_series_refs(args.series_csv)
    all_balls = []

    years_filter = set(args.years) if args.years else None

    failures: list[str] = []

    for ref in refs:
        if years_filter and ref.year not in years_filter:
            continue

        print(f"[series] {ref.year} -> {ref.url}")
        try:
            schedule_html = fetch_html(ref.url)
        except Exception as exc:  # noqa: BLE001
            msg = f"series {ref.year} failed: {exc}"
            failures.append(msg)
            print(f"  !! {msg}")
            continue

        match_urls = extract_match_urls(schedule_html)
        print(f"  found {len(match_urls)} match URLs")

        if args.max_matches_per_series:
            match_urls = match_urls[: args.max_matches_per_series]

        for idx, match_url in enumerate(match_urls, start=1):
            print(f"  [{idx}/{len(match_urls)}] scraping {match_url}")
            try:
                balls = scrape_match_commentary(
                    ipl_year=ref.year,
                    match_url=match_url,
                    sleep_seconds=args.sleep_seconds,
                )
            except Exception as exc:  # noqa: BLE001
                msg = f"match failed ({match_url}): {exc}"
                failures.append(msg)
                print(f"      !! {msg}")
                continue
            print(f"      extracted {len(balls)} commentary rows")
            all_balls.extend(balls)

    write_commentary_csv(args.output_csv, all_balls)
    print(f"Wrote {len(all_balls)} commentary rows to {args.output_csv}")
    if failures:
        print("Completed with failures:")
        for failure in failures:
            print(f"  - {failure}")


def cmd_build_pitchmap(args: argparse.Namespace) -> None:
    render_pitchmap_html(args.input_csv, args.output_html)
    print(f"Pitchmap HTML written to: {args.output_html}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IPL Pitchmap pipeline utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    series = sub.add_parser("series", help="Parse IPL series IDs from CSV list")
    series.add_argument("--csv", default=str(Path("data/ipl_series_urls.csv")))
    series.set_defaults(func=cmd_series)

    scrape = sub.add_parser(
        "scrape-full-commentary",
        help="Scrape match URLs from IPL season pages and extract commentary rows",
    )
    scrape.add_argument("--series-csv", default=str(Path("data/ipl_series_urls.csv")))
    scrape.add_argument("--output-csv", default=str(Path("data/ipl_commentary_full.csv")))
    scrape.add_argument(
        "--years",
        nargs="+",
        type=int,
        help="Optional list of years to scrape (example: --years 2023 2024)",
    )
    scrape.add_argument(
        "--max-matches-per-series",
        type=int,
        default=0,
        help="Optional cap for faster dry-runs (0 means no cap)",
    )
    scrape.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.5,
        help="Delay between match requests for polite scraping",
    )
    scrape.set_defaults(func=cmd_scrape_full_commentary)

    build = sub.add_parser("build-pitchmap", help="Build pitchmap HTML from commentary CSV")
    build.add_argument("--input-csv", default=str(Path("data/sample_commentary.csv")))
    build.add_argument("--output-html", default=str(Path("artifacts/pitchmap.html")))
    build.set_defaults(func=cmd_build_pitchmap)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
