import requests
import pandas as pd

API_KEY = "6995e5f307174fc7909a551bf2394bf0"  # ← tu clave

headers = {"X-Auth-Token": API_KEY}

# Códigos de ligas en football-data.org
LIGAS = {
    "PL": "Premier League",
    "CL": "Champions League", 
    "PD": "La Liga",
}

def obtener_partidos(liga_codigo, temporada):
    url = f"https://api.football-data.org/v4/competitions/{liga_codigo}/matches?season={temporada}&status=FINISHED"
    r = requests.get(url, headers=headers)
    datos = r.json()

    if "matches" not in datos:
        print(f"  ⚠️ Sin datos: {datos.get('message', 'error desconocido')}")
        return []

    partidos = []
    for p in datos["matches"]:
        goles_l = p["score"]["fullTime"]["home"]
        goles_v = p["score"]["fullTime"]["away"]
        if goles_l is None or goles_v is None:
            continue
        partidos.append({
            "liga": LIGAS[liga_codigo],
            "fecha": p["utcDate"][:10],
            "local": p["homeTeam"]["name"],
            "visitante": p["awayTeam"]["name"],
            "goles_local": goles_l,
            "goles_visitante": goles_v,
            "resultado": "L" if goles_l > goles_v else "E" if goles_l == goles_v else "V"
        })
    return partidos

# Descargamos todas las ligas y temporadas
todos = []
for codigo, nombre in LIGAS.items():
    for temporada in [2022, 2023, 2024]:
        print(f"Descargando {nombre} - Temporada {temporada}...")
        partidos = obtener_partidos(codigo, temporada)
        print(f"  → {len(partidos)} partidos obtenidos")
        todos += partidos

# Guardamos
df = pd.DataFrame(todos)
df.to_csv("partidos.csv", index=False)
print(f"\n✅ Total: {len(df)} partidos guardados en partidos.csv")
print(df.groupby("liga").size())