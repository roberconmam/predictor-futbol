import requests

API_KEY = "6995e5f307174fc7909a551bf2394bf0"  # ← reemplaza con tu clave

headers = {
    "X-Auth-Token": API_KEY
}

# Probamos la conexión
url = "https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED&limit=10"
respuesta = requests.get(url, headers=headers)
datos = respuesta.json()

# Mostramos los últimos partidos de Premier League
print("✅ Conexión exitosa! Últimos partidos de Premier League:\n")
for partido in datos["matches"]:
    local = partido["homeTeam"]["name"]
    visitante = partido["awayTeam"]["name"]
    goles_local = partido["score"]["fullTime"]["home"]
    goles_visitante = partido["score"]["fullTime"]["away"]
    fecha = partido["utcDate"][:10]
    print(f"{fecha} | {local} {goles_local} - {goles_visitante} {visitante}")