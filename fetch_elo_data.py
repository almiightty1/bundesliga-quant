import glob, os, sys
import pandas as pd
sys.path.append(os.path.dirname(__file__))
from config import DATA_DIR, normalize_team

EXTERNAL_DATA_DIR = "external_data/data"
BUNDESLIGA_DIVISION_CODE = "D1"

def find_matches_file():
    candidates = glob.glob(os.path.join(EXTERNAL_DATA_DIR, "*.csv"))
    match_files = [c for c in candidates if "match" in os.path.basename(c).lower()]
    return match_files[0]

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    df = pd.read_csv(find_matches_file(), low_memory=False)
    df_bl = df[df["Division"] == BUNDESLIGA_DIVISION_CODE].copy()
    keep_cols = [c for c in ["MatchDate", "HomeTeam", "AwayTeam", "HomeElo", "AwayElo",
                              "Form3Home", "Form3Away", "Form5Home", "Form5Away"] if c in df_bl.columns]
    df_bl = df_bl[keep_cols].copy()
    df_bl["HomeTeam"] = df_bl["HomeTeam"].apply(normalize_team)
    df_bl["AwayTeam"] = df_bl["AwayTeam"].apply(normalize_team)
    df_bl["MatchDate"] = pd.to_datetime(df_bl["MatchDate"])
    df_bl = df_bl.dropna(subset=["HomeElo", "AwayElo"])
    out_path = os.path.join(DATA_DIR, "bundesliga_elo_form.csv")
    df_bl.to_csv(out_path, index=False)
    print(f"Listo. {len(df_bl)} partidos con Elo real guardados en {out_path}")

if __name__ == "__main__":
    main()
