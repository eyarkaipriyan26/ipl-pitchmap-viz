import argparse
from pathlib import Path

from .url_pipeline import load_series_refs


def cmd_series(args: argparse.Namespace) -> None:
    refs = load_series_refs(args.csv)
    for ref in refs:
        print(f"{ref.year}: series_id={ref.series_id} url={ref.url}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IPL Pitchmap pipeline utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    series = sub.add_parser("series", help="Parse IPL series IDs from CSV list")
    series.add_argument("--csv", default=str(Path("data/ipl_series_urls.csv")))
    series.set_defaults(func=cmd_series)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
