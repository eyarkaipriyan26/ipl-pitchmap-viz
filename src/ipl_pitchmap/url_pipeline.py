import re
from dataclasses import dataclass


SERIES_ID_PATTERN = re.compile(r"/series/[^/]*-(?P<series_id>\d+)/")
MATCH_ID_PATTERN = re.compile(r"-(?P<match_id>\d+)(?:\?|$)")


@dataclass
class SeriesRef:
    year: int
    url: str
    series_id: str


def parse_series_id(series_url: str) -> str:
    match = SERIES_ID_PATTERN.search(series_url)
    if not match:
        raise ValueError(f"Could not parse series id from URL: {series_url}")
    return match.group("series_id")


def parse_match_id(match_url: str) -> str:
    match = MATCH_ID_PATTERN.search(match_url)
    if not match:
        raise ValueError(f"Could not parse match id from URL: {match_url}")
    return match.group("match_id")


def load_series_refs(csv_path: str) -> list[SeriesRef]:
    refs: list[SeriesRef] = []
    with open(csv_path, "r", encoding="utf-8") as handle:
        next(handle)  # header
        for line in handle:
            line = line.strip()
            if not line:
                continue
            year_text, url = line.split(",", 1)
            refs.append(SeriesRef(year=int(year_text), url=url, series_id=parse_series_id(url)))
    return refs
