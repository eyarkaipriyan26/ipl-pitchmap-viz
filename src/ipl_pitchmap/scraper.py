from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import asdict
from html import unescape
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .models import BallCommentary
from .url_pipeline import parse_match_id

BASE_URL = "https://www.espncricinfo.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

HREF_PATTERN = re.compile(r'href=["\'](?P<href>/[^"\']+)["\']', re.IGNORECASE)
NEXT_DATA_PATTERN = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(?P<data>.*?)</script>', re.DOTALL
)


def fetch_html(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:  # nosec: B310
        return response.read().decode("utf-8", errors="replace")


def extract_match_urls(series_schedule_html: str) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []

    for match in HREF_PATTERN.finditer(series_schedule_html):
        href = unescape(match.group("href"))
        if not href.startswith("/series/"):
            continue
        if "match-schedule-fixtures-and-results" in href:
            continue
        full = urljoin(BASE_URL, href.split("?")[0])

        try:
            parse_match_id(full)
        except ValueError:
            continue

        if full in seen:
            continue
        seen.add(full)
        results.append(full)

    return results


def build_commentary_url(match_url: str) -> str:
    base = match_url.split("?")[0].rstrip("/")
    suffixes = ["/full-scorecard", "/live-cricket-score", "/ball-by-ball-commentary"]
    for suffix in suffixes:
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    return f"{base}/ball-by-ball-commentary"


def _walk_json(node: Any, out_rows: list[dict[str, Any]]) -> None:
    if isinstance(node, dict):
        text_value = node.get("commentText") or node.get("text") or node.get("commentary")
        if isinstance(text_value, str) and text_value.strip():
            out_rows.append(node)

        for value in node.values():
            _walk_json(value, out_rows)
        return

    if isinstance(node, list):
        for item in node:
            _walk_json(item, out_rows)


def extract_commentary_rows(commentary_html: str) -> list[dict[str, Any]]:
    next_data_match = NEXT_DATA_PATTERN.search(commentary_html)
    if not next_data_match:
        return []

    raw_json = next_data_match.group("data")
    payload = json.loads(raw_json)

    rows: list[dict[str, Any]] = []
    _walk_json(payload, rows)

    unique: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for row in rows:
        text_value = str(row.get("commentText") or row.get("text") or row.get("commentary") or "").strip()
        over_ball = str(
            row.get("overNumber")
            or row.get("over")
            or row.get("overBall")
            or row.get("ball")
            or ""
        ).strip()
        dedupe_key = (over_ball, text_value)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        unique.append(row)

    return unique


def parse_commentary_balls(ipl_year: int, match_id: str, rows: list[dict[str, Any]]) -> list[BallCommentary]:
    balls: list[BallCommentary] = []
    for row in rows:
        text = str(row.get("commentText") or row.get("text") or row.get("commentary") or "").strip()
        if not text:
            continue

        over_ball = str(
            row.get("overNumber")
            or row.get("over")
            or row.get("overBall")
            or row.get("ball")
            or ""
        ).strip()

        bowler = ""
        bowler_dict = row.get("bowler")
        if isinstance(bowler_dict, dict):
            bowler = str(bowler_dict.get("longName") or bowler_dict.get("name") or "")
        elif isinstance(row.get("bowlerName"), str):
            bowler = row["bowlerName"]

        batter = ""
        batter_dict = row.get("batter") or row.get("batsman")
        if isinstance(batter_dict, dict):
            batter = str(batter_dict.get("longName") or batter_dict.get("name") or "")
        elif isinstance(row.get("batterName"), str):
            batter = row["batterName"]

        balls.append(
            BallCommentary(
                ipl_year=ipl_year,
                match_id=match_id,
                over_ball=over_ball,
                bowler=bowler,
                batter=batter,
                commentary=text,
            )
        )

    return balls


def scrape_match_commentary(ipl_year: int, match_url: str, sleep_seconds: float = 0.5) -> list[BallCommentary]:
    commentary_url = build_commentary_url(match_url)
    html = fetch_html(commentary_url)
    rows = extract_commentary_rows(html)
    match_id = parse_match_id(match_url)
    balls = parse_commentary_balls(ipl_year=ipl_year, match_id=match_id, rows=rows)
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    return balls


def write_commentary_csv(output_csv: str, balls: list[BallCommentary]) -> None:
    with open(output_csv, "w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "ipl_year",
            "match_id",
            "over_ball",
            "bowler",
            "batter",
            "batter_hand",
            "commentary",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for ball in balls:
            writer.writerow(asdict(ball))
