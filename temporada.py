import pandas as pd
from pathlib import Path

GOOD_FG = {"good", "made"}
GOOD_XP = {"good", "made", "success", "successful"}

CSV_FILE = "NFL Play by Play 2009-2018 (v5).csv"

def puntos_por_jugada(row):
    pts = 0
    td = row.get('touchdown')
    if pd.notna(td) and int(td) == 1:
        pts += 6
    xpr = row.get('extra_point_result')
    if isinstance(xpr, str) and xpr.strip().lower() in GOOD_XP:
        pts += 1
    fgr = row.get('field_goal_result')
    if isinstance(fgr, str) and fgr.strip().lower() in GOOD_FG:
        pts += 3
    sf = row.get('safety')
    if pd.notna(sf) and int(sf) == 1:
        pts += 2
    return pts

def tipo_jugada(row):
    td = row.get('touchdown')
    if pd.notna(td) and int(td) == 1:
        pt = str(row.get('play_type') or '').strip().lower()
        if pt == 'run':
            return 'corrida'
        elif pt == 'pass':
            return 'pase'
        else:
            return 'touchdown_otro'
    fgr = row.get('field_goal_result')
    if isinstance(fgr, str) and fgr.strip().lower() in GOOD_FG:
        return 'gol_de_campo'
    xpr = row.get('extra_point_result')
    if isinstance(xpr, str) and xpr.strip().lower() in GOOD_XP:
        return 'extra_point'
    sf = row.get('safety')
    if pd.notna(sf) and int(sf) == 1:
        return 'safety'
    return 'otro'

def extraer_hechos_prolog(temporada):
    temporada = int(temporada)

    path = Path(CSV_FILE)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {CSV_FILE}")

    USECOLS = [
        'game_id', 'game_date', 'away_team', 'home_team',
        'posteam', 'defteam',
        'qtr', 'play_type', 'touchdown', 'field_goal_result', 'extra_point_result', 'safety',
    ]

    juegos_map = {}
    puntos_map = {}
    anot_rows = []

    CHUNK = 200_000

    for chunk in pd.read_csv(
        path,
        usecols=USECOLS,
        chunksize=CHUNK,
        low_memory=True,
        on_bad_lines="skip",
        encoding_errors="ignore"
    ):
        dt = pd.to_datetime(chunk['game_date'], errors='coerce')
        yr = dt.dt.year
        mo = dt.dt.month
        season_vals = yr.where((mo >= 8) & (mo <= 12), yr - 1)
        chunk = chunk.assign(season=season_vals)

        chunk = chunk[chunk['season'] == temporada].copy()
        if chunk.empty:
            continue

        for _, r in (
            chunk[['game_id', 'game_date', 'away_team', 'home_team']]
            .dropna(subset=['game_id'])
            .drop_duplicates()
            .iterrows()
        ):
            gid = r['game_id']
            if gid not in juegos_map:
                juegos_map[gid] = (r['game_date'], r['away_team'], r['home_team'])

        chunk['puntos_jugada'] = chunk.apply(puntos_por_jugada, axis=1)
        sc = chunk[chunk['puntos_jugada'] > 0].copy()

        if not sc.empty:
            def equipo_anota(row):
                sf = row.get('safety')
                if pd.notna(sf) and int(sf) == 1:
                    return row.get('defteam')
                return row.get('posteam')

            sc['equipo_anota'] = sc.apply(equipo_anota, axis=1)
            sc_group = sc.groupby(['game_id', 'equipo_anota'], dropna=True)['puntos_jugada'].sum().reset_index()
            for _, r in sc_group.iterrows():
                key = (r['game_id'], r['equipo_anota'])
                puntos_map[key] = puntos_map.get(key, 0) + int(r['puntos_jugada'])

        anot_mask = (
            ((chunk['touchdown'].fillna(0)) == 1) |
            (chunk['field_goal_result'].astype(str).str.lower().isin(GOOD_FG)) |
            (chunk['extra_point_result'].astype(str).str.lower().isin(GOOD_XP)) |
            ((chunk['safety'].fillna(0)) == 1)
        )
        anot = chunk[anot_mask].copy()
        if not anot.empty:
            anot['tipo'] = anot.apply(tipo_jugada, axis=1)
            def equipo_anota_row(r):
                sf = r.get('safety')
                if pd.notna(sf) and int(sf) == 1:
                    return r.get('defteam')
                return r.get('posteam')
            anot['equipo_anota'] = anot.apply(equipo_anota_row, axis=1)

            for _, r in anot.iterrows():
                gid = r['game_id']
                if gid in juegos_map:
                    fecha, away, home = juegos_map[gid]
                    q = r['qtr']
                    cuarto = int(q) if pd.notna(q) else -1
                    equipo = str(r['equipo_anota']) if pd.notna(r['equipo_anota']) else 'UNKNOWN'
                    anot_rows.append({
                        'cuarto': cuarto,
                        'equipo': equipo,
                        'tipo':   str(r['tipo']),
                        'fecha':  str(fecha),
                        'away':   str(away),
                        'home':   str(home),
                    })

    if not juegos_map:
        raise RuntimeError(f"No se encontraron partidos para la temporada {temporada}. Revisa el CSV.")

    filas_partido = []
    for gid, (fecha, away, home) in juegos_map.items():
        pts_away = int(puntos_map.get((gid, away), 0))
        pts_home = int(puntos_map.get((gid, home), 0))
        filas_partido.append((fecha, away, home, pts_away, pts_home))

    out = f"temporada_{temporada}.pl"
    with open(out, "w", encoding="utf-8") as f:
        for fecha, away, home, pa, ph in filas_partido:
            f.write(f"partido('{fecha}', '{away}', '{home}', {pa}, {ph}).\n")
        f.write("\n")
        for r in anot_rows:
            f.write(
                f"anotacion({r['cuarto']}, '{r['equipo']}', '{r['tipo']}', "
                f"'{r['fecha']}', '{r['away']}', '{r['home']}').\n"
            )

    print(f"Hechos Prolog generados en {out}")

if __name__ == "__main__":
    temporada = input("Ingrese la temporada (ejemplo 2013): ").strip()
    extraer_hechos_prolog(temporada)
