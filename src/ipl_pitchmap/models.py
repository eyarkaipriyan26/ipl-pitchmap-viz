from dataclasses import dataclass
from typing import Optional


@dataclass
class BallCommentary:
    ipl_year: int
    match_id: str
    over_ball: str
    bowler: str
    batter: str
    commentary: str


@dataclass
class PitchCell:
    batter_hand: str  # RHB or LHB
    length_band: str  # 6 buckets
    line_band: str    # 5 buckets
    confidence: float
    reason: str


@dataclass
class MappedBall:
    ball: BallCommentary
    cell: Optional[PitchCell]
