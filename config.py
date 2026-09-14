"""
Configuración central del proyecto.

El problema #1 al combinar fuentes de datos de fútbol es que cada una
nombra a los equipos distinto. Este mapeo traduce todo a un nombre
canónico único que usaremos en todo el pipeline.
"""

# Nombre canónico -> variantes que aparecen en cada fuente
TEAM_NAME_MAP = {
    "Bayern Munich": ["Bayern Munich", "Bayern München", "FC Bayern München", "Bayern"],
    "Bayer Leverkusen": ["Bayer Leverkusen", "Leverkusen", "Bayer 04 Leverkusen"],
    "Borussia Dortmund": ["Borussia Dortmund", "Dortmund", "BVB"],
    "RB Leipzig": ["RB Leipzig", "RasenBallsport Leipzig", "Leipzig"],
    "VfB Stuttgart": ["VfB Stuttgart", "Stuttgart"],
    "Eintracht Frankfurt": ["Eintracht Frankfurt", "Ein Frankfurt", "Frankfurt"],
    "SC Freiburg": ["SC Freiburg", "Freiburg"],
    "TSG Hoffenheim": ["TSG Hoffenheim", "Hoffenheim"],
    "Werder Bremen": ["Werder Bremen", "Bremen"],
    "Borussia Monchengladbach": ["Borussia Monchengladbach", "M'gladbach", "Borussia M.Gladbach", "Gladbach"],
    "FC Augsburg": ["FC Augsburg", "Augsburg"],
    "Union Berlin": ["Union Berlin", "1. FC Union Berlin"],
    "FSV Mainz 05": ["FSV Mainz 05", "Mainz", "Mainz 05"],
    "VfL Wolfsburg": ["VfL Wolfsburg", "Wolfsburg"],
    "1. FC Koln": ["1. FC Koln", "FC Koln", "Koeln", "Köln", "1.FC Koeln"],
    "FC St. Pauli": ["FC St. Pauli", "St Pauli", "St. Pauli"],
    "Holstein Kiel": ["Holstein Kiel", "Kiel"],
    "1. FC Heidenheim": ["1. FC Heidenheim", "Heidenheim"],
    "SV Darmstadt 98": ["SV Darmstadt 98", "Darmstadt"],
    "VfL Bochum": ["VfL Bochum", "Bochum"],
    "Hamburger SV": ["Hamburger SV", "Hamburg", "HSV"],
}


def build_reverse_lookup() -> dict:
    """Devuelve {variante: nombre_canonico} para lookup O(1)."""
    reverse = {}
    for canonical, variants in TEAM_NAME_MAP.items():
        for v in variants:
            reverse[v] = canonical
    return reverse


REVERSE_TEAM_LOOKUP = build_reverse_lookup()


def normalize_team(name: str) -> str:
    """Traduce cualquier variante conocida al nombre canónico.
    Si no se reconoce, devuelve el nombre original y avisa por consola
    (así detectas equipos nuevos, ascensos/descensos, que faltan mapear)."""
    if name in REVERSE_TEAM_LOOKUP:
        return REVERSE_TEAM_LOOKUP[name]
    print(f"[AVISO] Equipo no mapeado: '{name}' -> revisa TEAM_NAME_MAP en config.py")
    return name


# football-data.co.uk: código de división Bundesliga 1 = D1
FOOTBALL_DATA_DIVISION = "D1"

# Temporadas a descargar, formato AABB (ej. 2324 = temporada 2023-24)
FOOTBALL_DATA_SEASONS = ["2223", "2324", "2425", "2526"]

# understat.com usa el año de inicio de temporada
UNDERSTAT_LEAGUE = "Bundesliga"
UNDERSTAT_SEASONS = [2022, 2023, 2024, 2025]

DATA_DIR = "data"
