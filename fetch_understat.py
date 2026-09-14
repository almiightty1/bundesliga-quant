"""
Extrae datos de xG (Expected Goals) REALES por partido desde understat.com.

understat.com no tiene una API pública documentada, pero incrusta los datos
del partido como JSON dentro de un <script> en la página de cada liga/temporada
(variable JS `datesData`). Este script localiza ese bloque, lo decodifica y lo
convierte en un DataFrame.

Esto es scraping de una página pública para uso propio de análisis, no
redistribución del contenido de terceros.

Uso:
    python src/fetch_understat.py
"""

import json
import os
import re
import sys

import pandas as pd
import requests

sys.path.append(os.path.dirname(__file__))
from config import DATA_DIR, UNDERSTAT_LEAGUE, UNDERSTAT_SEASONS, normalize_team

BASE_URL = "https://understat.com/league/{league}/{season}"


def extract_json_var(html: str, var_name: str) -> list:
    """Busca `var datesData = JSON.parse('...escaped json...')` y lo decodifica."""
    pattern = re.compile(
        rf"var\s+{var_name}\s*=\s*JSON\.parse\('(.+?)'\)", re.DOTALL
    )
    match = pattern.search(html)
    if not match:
        raise ValueError(f"No se encontró la variable '{var_name}' en la página. "
                          f"understat pudo haber cambiado su estructura HTML.")
    raw = match.group(1)
    # El JSON viene con caracteres escapados tipo \xXX (unicode-escape)
    decoded = raw.encode("utf-8").decode("unicode_escape").encode("latin1").decode("utf-8")
    return json.loads(decoded)


def fetch_season(league: str, season: int) -> pd.DataFrame:
    url = BASE_URL.format(league=league, season=season)
    print(f"Descargando {url} ...")
    headers = {"User-Agent": "Mozilla/5.0 (research script)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    matches = extract_json_var(resp.text, "datesData")

    rows = []
    for m in matches:
        # Partidos aún no jugados traen goals/xG en None
        if m.get("isResult") is not True:
            continue
        home = m["h"]["title"]
        away = m["a"]["title"]
        rows.append({
            "Season": season,
            "Date": m["datetime"],
            "HomeTeam": normalize_team(home),
            "AwayTeam": normalize_team(away),
            "xG_Home": float(m["xG"]["h"]),
            "xG_Away": float(m["xG"]["a"]),
            "Goals_Home": int(m["goals"]["h"]),
            "Goals_Away": int(m["goals"]["a"]),
        })

    return pd.DataFrame(rows)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    all_seasons = []

    for season in UNDERSTAT_SEASONS:
        try:
            df = fetch_season(UNDERSTAT_LEAGUE, season)
            all_seasons.append(df)
        except Exception as e:
            print(f"  [ERROR] No se pudo obtener la temporada {season}: {e}")

    if not all_seasons:
        print("No se obtuvo ninguna temporada de understat.")
        return

    full_df = pd.concat(all_seasons, ignore_index=True)
    full_df["Date"] = pd.to_datetime(full_df["Date"])
    full_df = full_df.sort_values("Date").reset_index(drop=True)

    out_path = os.path.join(DATA_DIR, "bundesliga_xg_history.csv")
    full_df.to_csv(out_path, index=False)
    print(f"\nListo. {len(full_df)} partidos con xG guardados en {out_path}")
    print(full_df.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
