import math
from typing import List, Dict
from app.schemas import InningsSummaryRequest, InningsSummaryResponse, BatterSummary, BowlerSummary

class InningsCalculatorService:

    @staticmethod
    def calculate_summary(data: InningsSummaryRequest) -> InningsSummaryResponse:
        total_runs = 0
        wickets_lost = 0
        legal_balls = 0
        recent_balls_log: List[str] = []

        batters: Dict[str, dict] = {}
        bowlers: Dict[str, dict] = {}

        for event in data.events:
            # Calculate total runs
            event_total_runs = event.runs_scored + event.extras_runs
            total_runs += event_total_runs

            # Determine legal ball
            is_legal = event.extras_type not in ["wide", "noball"]
            if is_legal:
                legal_balls += 1

            # Log recent ball text
            if event.is_wicket:
                recent_balls_log.append("W")
            elif event.extras_type:
                recent_balls_log.append(f"{event_total_runs}{event.extras_type[0].upper()}")
            else:
                recent_balls_log.append(str(event.runs_scored))

            # --- BATTER METRICS ---
            if event.batter_id not in batters:
                batters[event.batter_id] = {
                    "name": event.batter_name,
                    "runs": 0,
                    "balls_faced": 0,
                    "fours": 0,
                    "sixes": 0,
                    "is_out": False
                }
            
            # Runs off the bat (extras like wides/byes do not count to batter runs)
            if event.extras_type not in ["wide", "bye", "legbye"]:
                batters[event.batter_id]["runs"] += event.runs_scored

            if is_legal:
                batters[event.batter_id]["balls_faced"] += 1

            if event.runs_scored == 4 and event.extras_type is None:
                batters[event.batter_id]["fours"] += 1
            elif event.runs_scored == 6 and event.extras_type is None:
                batters[event.batter_id]["sixes"] += 1

            # --- BOWLER METRICS ---
            if event.bowler_id not in bowlers:
                bowlers[event.bowler_id] = {
                    "name": event.bowler_name,
                    "legal_balls": 0,
                    "runs_conceded": 0,
                    "wickets": 0
                }

            if is_legal:
                bowlers[event.bowler_id]["legal_balls"] += 1

            # Wides and No-balls count against bowler runs
            if event.extras_type in [None, "wide", "noball"]:
                bowlers[event.bowler_id]["runs_conceded"] += event_total_runs

            # --- WICKETS ---
            if event.is_wicket:
                wickets_lost += 1
                if event.wicket_type != "run_out":
                    bowlers[event.bowler_id]["wickets"] += 1

                dismissed_id = event.dismissed_batter_id or event.batter_id
                if dismissed_id in batters:
                    batters[dismissed_id]["is_out"] = True

        # Helper calculations
        overs_completed = legal_balls // 6
        remaining_balls = legal_balls % 6
        overs_formatted = float(f"{overs_completed}.{remaining_balls}")
        overs_decimal = legal_balls / 6.0 if legal_balls > 0 else 0.0

        run_rate = round(total_runs / overs_decimal, 2) if overs_decimal > 0 else 0.0

        # Construct Batter Summary List
        batter_summaries = []
        for b_id, b_data in batters.items():
            sr = round((b_data["runs"] / b_data["balls_faced"]) * 100, 2) if b_data["balls_faced"] > 0 else 0.0
            batter_summaries.append(
                BatterSummary(
                    batter_id=b_id,
                    batter_name=b_data["name"],
                    runs=b_data["runs"],
                    balls_faced=b_data["balls_faced"],
                    fours=b_data["fours"],
                    sixes=b_data["sixes"],
                    strike_rate=sr,
                    is_out=b_data["is_out"]
                )
            )

        # Construct Bowler Summary List
        bowler_summaries = []
        for bw_id, bw_data in bowlers.items():
            bw_overs_comp = bw_data["legal_balls"] // 6
            bw_rem_balls = bw_data["legal_balls"] % 6
            bw_overs = float(f"{bw_overs_comp}.{bw_rem_balls}")
            bw_overs_dec = bw_data["legal_balls"] / 6.0 if bw_data["legal_balls"] > 0 else 0.0
            econ = round(bw_data["runs_conceded"] / bw_overs_dec, 2) if bw_overs_dec > 0 else 0.0

            bowler_summaries.append(
                BowlerSummary(
                    bowler_id=bw_id,
                    bowler_name=bw_data["name"],
                    overs=bw_overs,
                    runs_conceded=bw_data["runs_conceded"],
                    wickets=bw_data["wickets"],
                    economy_rate=econ
                )
            )

        return InningsSummaryResponse(
            innings_id=data.innings_id,
            team_name=data.team_name,
            total_runs=total_runs,
            wickets_lost=wickets_lost,
            legal_balls=legal_balls,
            overs=overs_formatted,
            run_rate=run_rate,
            batting_performances=batter_summaries,
            bowling_performances=bowler_summaries,
            recent_balls=recent_balls_log[-6:]  # Last 6 balls
        )