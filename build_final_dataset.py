import os, sys
import pandas as pd
sys.path.append(os.path.dirname(__file__))
from config import DATA_DIR

def main():
    odds = pd.read_csv(os.path.join(DATA_DIR, "bundesliga_odds_history.csv"), parse_dates=["Date"])
    elo = pd.read_csv(os.path.join(DATA_DIR, "bundesliga_elo_form.csv"), parse_dates=["MatchDate"])
    odds["match_day"] = odds["Date"].dt.date
    elo["match_day"] = elo["MatchDate"].dt.date
    merged = pd.merge(
        odds,
        elo[["match_day", "HomeTeam", "AwayTeam", "HomeElo", "AwayElo",
             "Form3Home", "Form3Away", "Form5Home", "Form5Away"]],
        on=["match_day", "HomeTeam", "AwayTeam"], how="inner",
    )
    merged = merged.drop(columns=["match_day"])
    out_path = os.path.join(DATA_DIR, "bundesliga_dataset_final.csv")
    merged.to_csv(out_path, index=False)
    print(f"Dataset final: {len(merged)} partidos con cuotas + Elo real guardados en {out_path}")

if __name__ == "__main__":
    main()
