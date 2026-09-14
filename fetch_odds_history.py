"""
Descarga históricos de resultados + cuotas de cierre de football-data.co.uk
para la Bundesliga.

Estos datos son GRATIS, no requieren API key, e incluyen columnas de:
- Resultado y estadísticas del partido (goles, tiros, córners, tarjetas)
- Cuotas de varias casas, incluida Pinnacle (PSH/PSD/PSA), que es el
  benchmark que usaremos para medir si un modelo realmente tiene edge
  (closing line value).

Uso:
    python src/fetch_odds_history.py
"""

import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.dirname(__file__))
from config import DATA_DIR, FOOTBALL_DATA_DIVISION, FOOTBALL_DATA_SEASONS, normalize_team

BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{division}.csv"


def download_season(season: str, division: str = FOOTBALL_DATA_DIVISION) -> pd.DataFrame:
    url = BASE_URL.format(season=season, division=division)
    print(f"Descargando {url} ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    from io import StringIO
    # football-data.co.uk a veces usa encoding latin-1
    try:
        df = pd.read_csv(StringIO(resp.content.decode("utf-8")))
    except UnicodeDecodeError:
        df = pd.read_csv(StringIO(resp.content.decode("latin-1")))

    df["Season"] = season
    return df


def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    # Nos quedamos solo con columnas que existen en todas las temporadas
    keep_cols = [
        "Season", "Date", "HomeTeam", "AwayTeam",
        "FTHG", "FTAG", "FTR",
        "HS", "AS", "HST", "AST",
        "HC", "AC",       # córners
        "HY", "AY", "HR", "AR",  # tarjetas
        "B365H", "B365D", "B365A",   # bet365 (referencia de mercado blando)
        "PSH", "PSD", "PSA",         # Pinnacle cierre (referencia sharp)
    ]
    available = [c for c in keep_cols if c in df.columns]
    missing = set(keep_cols) - set(available)
    if missing:
        print(f"  (columnas no disponibles en esta temporada, se omiten: {missing})")

    df = df[available].copy()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["HomeTeam"] = df["HomeTeam"].apply(normalize_team)
    df["AwayTeam"] = df["AwayTeam"].apply(normalize_team)
    return df


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    all_seasons = []

    for season in FOOTBALL_DATA_SEASONS:
        try:
            raw = download_season(season)
            clean = clean_and_normalize(raw)
            all_seasons.append(clean)
        except Exception as e:
            print(f"  [ERROR] No se pudo descargar la temporada {season}: {e}")

    if not all_seasons:
        print("No se descargó ninguna temporada. Revisa tu conexión o los códigos de temporada.")
        return

    full_df = pd.concat(all_seasons, ignore_index=True)
    full_df = full_df.sort_values("Date").reset_index(drop=True)

    out_path = os.path.join(DATA_DIR, "bundesliga_odds_history.csv")
    full_df.to_csv(out_path, index=False)
    print(f"\nListo. {len(full_df)} partidos guardados en {out_path}")
    print(full_df.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
