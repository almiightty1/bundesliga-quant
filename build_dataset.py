"""
Combina bundesliga_odds_history.csv (resultados + cuotas) con
bundesliga_xg_history.csv (xG real) en un único dataset limpio,
listo para calibrar un modelo y para backtesting.

Requiere haber corrido antes:
    python src/fetch_odds_history.py
    python src/fetch_understat.py

Uso:
    python src/build_dataset.py
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(__file__))
from config import DATA_DIR


def main():
    odds_path = os.path.join(DATA_DIR, "bundesliga_odds_history.csv")
    xg_path = os.path.join(DATA_DIR, "bundesliga_xg_history.csv")

    if not os.path.exists(odds_path) or not os.path.exists(xg_path):
        print("Faltan archivos fuente. Corre primero fetch_odds_history.py y fetch_understat.py")
        return

    odds = pd.read_csv(odds_path, parse_dates=["Date"])
    xg = pd.read_csv(xg_path, parse_dates=["Date"])

    # El cruce se hace por equipos + fecha. Como las fuentes pueden reportar
    # la fecha con horas distintas, cruzamos solo por el día.
    odds["match_day"] = odds["Date"].dt.date
    xg["match_day"] = xg["Date"].dt.date

    merged = pd.merge(
        odds,
        xg[["match_day", "HomeTeam", "AwayTeam", "xG_Home", "xG_Away"]],
        on=["match_day", "HomeTeam", "AwayTeam"],
        how="inner",
    )

    unmatched = len(odds) - len(merged)
    if unmatched > 0:
        print(f"[AVISO] {unmatched} partidos de cuotas no encontraron xG correspondiente "
              f"(revisa TEAM_NAME_MAP o desfases de fecha).")

    merged = merged.drop(columns=["match_day"])
    out_path = os.path.join(DATA_DIR, "bundesliga_dataset.csv")
    merged.to_csv(out_path, index=False)

    print(f"\nDataset final: {len(merged)} partidos con cuotas + xG reales.")
    print(f"Guardado en {out_path}")
    print(merged.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
