# Bundesliga Quant — Pipeline de Datos Reales

Esta es la base de datos real sobre la que vamos a construir el modelo.
Sin esto, cualquier "detección de value bets" es solo apariencia.

## Qué hace

1. **`src/fetch_odds_history.py`** — descarga resultados y cuotas históricas
   (incluidas las de Pinnacle, `PSH/PSD/PSA`) desde football-data.co.uk.
   Gratis, sin API key.
2. **`src/fetch_understat.py`** — extrae xG real por partido desde
   understat.com (scraping de la página pública).
3. **`src/build_dataset.py`** — cruza ambas fuentes por equipo + fecha y
   genera `data/bundesliga_dataset.csv`, el dataset limpio final.

Los nombres de equipo se normalizan usando `src/config.py::TEAM_NAME_MAP`,
porque cada fuente los escribe distinto (`Bayern Munich` vs `Bayern München`,
etc). **Cuando el script avise `[AVISO] Equipo no mapeado`, agrega esa
variante al diccionario.**

## Cómo correrlo

```bash
pip install -r requirements.txt
python src/fetch_odds_history.py
python src/fetch_understat.py
python src/build_dataset.py
```

Esto te deja tres CSV en `data/`:
- `bundesliga_odds_history.csv`
- `bundesliga_xg_history.csv`
- `bundesliga_dataset.csv` ← este es el que usaremos para lo siguiente

## Notas importantes

- **No pude probar el scraping en vivo** (mi entorno de trabajo no tiene
  acceso a internet). Corre estos scripts en tu máquina o en GitHub Actions
  y pégame cualquier error tal cual salga en consola — lo ajustamos.
- understat puede cambiar su HTML sin aviso; si `fetch_understat.py` falla
  con "No se encontró la variable 'datesData'", es la primera señal de que
  cambiaron algo y hay que revisar la estructura de la página.
- **Nunca subas tu API key a un repo público.** Este pipeline no necesita
  ninguna (ambas fuentes son públicas), pero cuando conectemos The Odds API
  para cuotas en vivo, esa key va en `st.secrets`, no en el código.

## Siguiente paso

Con `bundesliga_dataset.csv` armado, lo que sigue es:
1. Calibrar un modelo Dixon-Coles (fuerza de ataque/defensa por equipo +
   decaimiento temporal) usando este dataset.
2. Backtestear ese modelo contra las cuotas de cierre de Pinnacle para medir
   si de verdad tiene edge, antes de conectarlo a cuotas en vivo.

Avísame cuando tengas `bundesliga_dataset.csv` generado (o si algún script
falla) y seguimos con el motor de backtesting.
