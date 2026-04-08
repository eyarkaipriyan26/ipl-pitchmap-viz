from __future__ import annotations

import re

from .models import BallCommentary, MappedBall, PitchCell

LENGTH_PATTERNS = [
    ("Full Toss", [r"full toss"]),
    ("Yorker", [r"yorker", r"blockhole"]),
    ("Full Length", [r"full(?!\s*toss)", r"pitched up", r"half-volley"]),
    ("Good Length", [r"good length"]),
    ("Short of Good Length", [r"back of a length", r"short of good length"]),
    ("Short Length", [r"short", r"bouncer"]),
]

LINE_PATTERNS = [
    ("Wide Outside Off", [r"wide outside off", r"fifth stump"]),
    ("Outside Off", [r"outside off", r"just outside off"]),
    ("Off Stump", [r"on off", r"off stump"]),
    ("Middle/Leg", [r"middle", r"on leg", r"leg stump"]),
    ("Far Leg", [r"down leg", r"well down leg"]),
]


def _extract_band(text: str, rules: list[tuple[str, list[str]]]) -> tuple[str | None, str | None]:
    lowered = text.lower()
    for band, patterns in rules:
        for pat in patterns:
            if re.search(pat, lowered):
                return band, pat
    return None, None


def map_commentary_ball(ball: BallCommentary, batter_hand: str = "RHB") -> MappedBall:
    length_band, length_hit = _extract_band(ball.commentary, LENGTH_PATTERNS)
    line_band, line_hit = _extract_band(ball.commentary, LINE_PATTERNS)

    if not length_band and not line_band:
        return MappedBall(ball=ball, cell=None)

    confidence = 0.2
    reason_parts = []
    if length_band:
        confidence += 0.4
        reason_parts.append(f"length:{length_hit}")
    if line_band:
        confidence += 0.4
        reason_parts.append(f"line:{line_hit}")

    if confidence > 1.0:
        confidence = 1.0

    cell = PitchCell(
        batter_hand=batter_hand,
        length_band=length_band or "UNKNOWN_LENGTH",
        line_band=line_band or "UNKNOWN_LINE",
        confidence=round(confidence, 2),
        reason=";".join(reason_parts),
    )
    return MappedBall(ball=ball, cell=cell)
