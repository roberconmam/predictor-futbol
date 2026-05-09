import requests
import pandas as pd

API_KEY = "6995e5f307174fc7909a551bf2394bf0"  # ← tu clave

headers = {"X-Auth-Token": API_KEY}

def obtener_partidos(temporada):
    url = f"https://api.football-data.org/v4/competitions/PL/matches?season={temporada}&status=FINISHED"
    r = requests.get(url, headers=headers)
    datos = r.json()

    # Verificamos qué nos devuelve la API
    if "matches" not in datos:
        print(f"⚠️ Error en temporada {temporada}:", datos)
        return []

    partidos = []
    for p in datos["matches"]:
        goles_l = p["score"]["fullTime"]["home"]
        goles_v = p["score"]["fullTime"]["away"]
        if goles_l is None or goles_v is None:
            continue
        partidos.append({
            "fecha": p["utcDate"][:10],
            "local": p["homeTeam"]["name"],
            "visitante": p["awayTeam"]["name"],
            "goles_local": goles_l,
            "goles_visitante": goles_v,
            "resultado": "L" if goles_l > goles_v else "E" if goles_l == goles_v else "V"
        })
    return partidos

# Descargamos temporadas
todos = []
for temporada in [2022, 2023, 2024]:
    print(f"Descargando temporada {temporada}...")
    partidos = obtener_partidos(temporada)
    print(f"   → {len(partidos)} partidos obtenidos")
    todos += partidos

# Guardamos
df = pd.DataFrame(todos)
df.to_csv("partidos.csv", index=False)
print(f"\n✅ Listo! Se guardaron {len(df)} partidos en partidos.csv")
print(df.head(10))