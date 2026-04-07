import argparse
from pathlib import Path

from .pitchmap_viz import render_pitchmap_html
from .url_pipeline import load_series_refs


def cmd_series(args: argparse.Namespace) -> None:
    refs = load_series_refs(args.csv)
    for ref in refs:
        print(f"{ref.year}: series_id={ref.series_id} url={ref.url}")


def cmd_build_pitchmap(args: argparse.Namespace) -> None:
    render_pitchmap_html(args.input_csv, args.output_html)
    print(f"Pitchmap HTML written to: {args.output_html}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IPL Pitchmap pipeline utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    series = sub.add_parser("series", help="Parse IPL series IDs from CSV list")
    series.add_argument("--csv", default=str(Path("data/ipl_series_urls.csv")))
    series.set_defaults(func=cmd_series)

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
