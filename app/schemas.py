from pydantic import BaseModel, Field
from typing import List, Optional

# --- INPUT SCHEMAS ---

class BallEventInput(BaseModel):
    ball_number: float = Field(..., example=0.1, description="Format: Over.Ball (e.g., 0.1, 1.4)")
    batter_id: str = Field(..., example="BAT_101")
    batter_name: str = Field(..., example="Virat Kohli")
    bowler_id: str = Field(..., example="BOWL_201")
    bowler_name: str = Field(..., example="Jasprit Bumrah")
    runs_scored: int = Field(..., ge=0, example=4)
    extras_type: Optional[str] = Field(None, example="wide", description="wide, noball, bye, legbye, or None")
    extras_runs: int = Field(0, ge=0, example=1)
    is_wicket: bool = Field(False)
    wicket_type: Optional[str] = Field(None, example="caught")
    dismissed_batter_id: Optional[str] = Field(None)

class InningsSummaryRequest(BaseModel):
    innings_id: str = Field(..., example="INN_2026_001")
    team_name: str = Field(..., example="India")
    events: List[BallEventInput] = Field(..., description="Raw ball-by-ball event log for the innings")


# --- OUTPUT SCHEMAS ---

class BatterSummary(BaseModel):
    batter_id: str
    batter_name: str
    runs: int
    balls_faced: int
    fours: int
    sixes: int
    strike_rate: float
    is_out: bool

class BowlerSummary(BaseModel):
    bowler_id: str
    bowler_name: str
    overs: float
    runs_conceded: int
    wickets: int
    economy_rate: float

class InningsSummaryResponse(BaseModel):
    innings_id: str
    team_name: str
    total_runs: int
    wickets_lost: int
    legal_balls: int
    overs: float
    run_rate: float
    batting_performances: List[BatterSummary]
    bowling_performances: List[BowlerSummary]
    recent_balls: List[str]