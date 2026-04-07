from __future__ import annotations

import csv
import html
from collections import defaultdict
from pathlib import Path

from .models import BallCommentary
from .pitch_mapper import map_commentary_ball

LENGTH_ORDER = [
    "Full Toss",
    "Yorker",
    "Full Length",
    "Good Length",
    "Short of Good Length",
    "Short Length",
]

LINE_ORDER = [
    "Wide Outside Off",
    "Outside Off",
    "Off Stump",
    "Middle/Leg",
    "Far Leg",
]


def load_commentary_csv(path: str) -> list[BallCommentary]:
    balls: list[BallCommentary] = []
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            balls.append(
                BallCommentary(
                    ipl_year=int(row["ipl_year"]),
                    match_id=row["match_id"],
                    over_ball=row["over_ball"],
                    bowler=row.get("bowler", ""),
                    batter=row.get("batter", ""),
                    commentary=row["commentary"],
                    batter_hand=row.get("batter_hand", "RHB") or "RHB",
                )
            )
    return balls


def _color_for_score(score: float, max_score: float) -> str:
    if max_score <= 0:
        return "#f5f5f5"
    ratio = score / max_score
    if ratio < 0.2:
        return "#fee8c8"
    if ratio < 0.4:
        return "#fdbb84"
    if ratio < 0.6:
        return "#fc8d59"
    if ratio < 0.8:
        return "#e34a33"
    return "#b30000"


def aggregate_grid(commentary_balls: list[BallCommentary]) -> dict[str, dict[tuple[str, str], float]]:
    aggregates: dict[str, dict[tuple[str, str], float]] = {
        "RHB": defaultdict(float),
        "LHB": defaultdict(float),
    }

    for ball in commentary_balls:
        mapped = map_commentary_ball(ball, batter_hand=ball.batter_hand)
        if mapped.cell is None:
            continue

        hand = mapped.cell.batter_hand
        if hand not in aggregates:
            aggregates[hand] = defaultdict(float)

        key = (mapped.cell.length_band, mapped.cell.line_band)
        aggregates[hand][key] += mapped.cell.confidence

    return aggregates


def _draw_grid(title: str, values: dict[tuple[str, str], float], max_score: float) -> str:
    cell_w = 58
    cell_h = 58
    x0 = 160
    y0 = 80

    out = [f'<text x="{x0 + 145}" y="35" font-size="26" text-anchor="middle">{title}</text>']

    for i, line in enumerate(LINE_ORDER):
        x = x0 + i * cell_w + (cell_w / 2)
        out.append(f'<text x="{x}" y="60" text-anchor="middle" font-size="14">{html.escape(line)}</text>')

    for j, length in enumerate(LENGTH_ORDER):
        y = y0 + j * cell_h + (cell_h / 2) + 5
        out.append(f'<text x="145" y="{y}" text-anchor="end" font-size="16">{html.escape(length)}</text>')

        for i, line in enumerate(LINE_ORDER):
            x = x0 + i * cell_w
            cell_val = values.get((length, line), 0.0)
            color = _color_for_score(cell_val, max_score)
            out.append(
                f'<rect x="{x}" y="{y0 + j * cell_h}" width="{cell_w}" height="{cell_h}" '
                f'stroke="#d9d9d9" fill="{color}"/>'
            )
            if cell_val > 0:
                out.append(
                    f'<text x="{x + cell_w/2}" y="{y0 + j*cell_h + cell_h/2 + 4}" '
                    f'text-anchor="middle" font-size="14" fill="#111">{cell_val:.1f}</text>'
                )

    return "\n".join(out)


def render_pitchmap_html(commentary_csv_path: str, output_html_path: str) -> None:
    balls = load_commentary_csv(commentary_csv_path)
    aggregates = aggregate_grid(balls)
    max_score = max(
        [0.0] + [score for hand_values in aggregates.values() for score in hand_values.values()]
    )

    rhb_svg = _draw_grid("RHB", aggregates.get("RHB", {}), max_score)
    lhb_svg = _draw_grid("LHB", aggregates.get("LHB", {}), max_score)

    html_text = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>IPL Pitchmap</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .row {{ display: flex; gap: 40px; }}
    .card {{ border: 1px solid #eee; border-radius: 8px; padding: 8px; }}
    .meta {{ color: #666; margin-top: 8px; }}
  </style>
</head>
<body>
  <h1>IPL Pitchmap (Commentary-derived)</h1>
  <p>6x5 grid from commentary text. Cell intensity = confidence-weighted volume.</p>
  <div class=\"row\">
    <div class=\"card\"><svg width=\"480\" height=\"460\">{rhb_svg}</svg></div>
    <div class=\"card\"><svg width=\"480\" height=\"460\">{lhb_svg}</svg></div>
  </div>
  <p class=\"meta\">Input file: {html.escape(commentary_csv_path)}</p>
</body>
</html>
"""

    out = Path(output_html_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
