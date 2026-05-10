import requests

WEATHER_API_KEY = "2c77037bbe6864dd76ae78fd4aed1cbf"  # ← tu clave de OpenWeather

# Ciudades donde juega cada equipo
CIUDADES_EQUIPOS = {
    # Premier League
    "Arsenal FC": "London,UK",
    "Chelsea FC": "London,UK",
    "Liverpool FC": "Liverpool,UK",
    "Manchester City FC": "Manchester,UK",
    "Manchester United FC": "Manchester,UK",
    "Tottenham Hotspur FC": "London,UK",
    "Newcastle United FC": "Newcastle,UK",
    "Aston Villa FC": "Birmingham,UK",
    "Brighton & Hove Albion FC": "Brighton,UK",
    "West Ham United FC": "London,UK",
    "Brentford FC": "London,UK",
    "Fulham FC": "London,UK",
    "Everton FC": "Liverpool,UK",
    "AFC Bournemouth": "Bournemouth,UK",
    "Nottingham Forest FC": "Nottingham,UK",
    "Wolverhampton Wanderers FC": "Wolverhampton,UK",
    "Crystal Palace FC": "London,UK",
    "Sunderland AFC": "Sunderland,UK",
    "Leeds United FC": "Leeds,UK",
    "Burnley FC": "Burnley,UK",
    # La Liga
    "FC Barcelona": "Barcelona,ES",
    "Real Madrid CF": "Madrid,ES",
    "Club Atlético de Madrid": "Madrid,ES",
    "Real Sociedad de Fútbol": "San Sebastian,ES",
    "Athletic Club": "Bilbao,ES",
    "Villarreal CF": "Villarreal,ES",
    "RC Celta de Vigo": "Vigo,ES",
    "Sevilla FC": "Seville,ES",
    "Valencia CF": "Valencia,ES",
    "Real Betis Balompié": "Seville,ES",
    "Getafe CF": "Madrid,ES",
    "Deportivo Alavés": "Vitoria,ES",
    "Rayo Vallecano de Madrid": "Madrid,ES",
    "UD Las Palmas": "Las Palmas,ES",
    "CA Osasuna": "Pamplona,ES",
    "Girona FC": "Girona,ES",
    "RCD Mallorca": "Palma,ES",
    "RCD Espanyol de Barcelona": "Barcelona,ES",
    "Elche CF": "Elche,ES",
    "Cádiz CF": "Cadiz,ES",
    # Champions League
    "Bayern München": "Munich,DE",
    "Paris Saint-Germain FC": "Paris,FR",
    "Juventus FC": "Turin,IT",
    "Borussia Dortmund": "Dortmund,DE",
    "Inter Milan": "Milan,IT",
    "AC Milan": "Milan,IT",
    "AFC Ajax": "Amsterdam,NL",
    "FC Porto": "Porto,PT",
    "SL Benfica": "Lisbon,PT",
    "Sporting CP": "Lisbon,PT",
    "SSC Napoli": "Naples,IT",
    "RB Leipzig": "Leipzig,DE",
    "FC Red Bull Salzburg": "Salzburg,AT",
}

def obtener_clima(equipo_local):
    ciudad = CIUDADES_EQUIPOS.get(equipo_local, "London,UK")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
    
    try:
        r = requests.get(url, timeout=5)
        datos = r.json()
        
        if r.status_code != 200:
            return None
        
        descripcion = datos["weather"][0]["description"]
        temperatura = datos["main"]["temp"]
        viento = datos["wind"]["speed"]
        lluvia = "rain" in datos["weather"][0]["main"].lower()
        nieve = "snow" in datos["weather"][0]["main"].lower()
        
        # Determinamos condición para el modelo
        if nieve or lluvia:
            condicion = "Lluvia 🌧️"
            factor = 0.93
        elif viento > 10:
            condicion = "Viento fuerte 💨"
            factor = 0.95
        else:
            condicion = "Bueno ☀️"
            factor = 1.0
        
        return {
            "ciudad": ciudad,
            "descripcion": descripcion.capitalize(),
            "temperatura": round(temperatura, 1),
            "viento": round(viento, 1),
            "condicion": condicion,
            "factor": factor
        }
    except:
        return None

if __name__ == "__main__":
    print("🌤️ Probando skill de clima...\n")
    equipos_prueba = ["Arsenal FC", "FC Barcelona", "Real Madrid CF", "Bayern München"]
    for equipo in equipos_prueba:
        clima = obtener_clima(equipo)
        if clima:
            print(f"🏟️ {equipo} ({clima['ciudad']})")
            print(f"   🌡️ {clima['temperatura']}°C — {clima['descripcion']}")
            print(f"   💨 Viento: {clima['viento']} m/s")
            print(f"   ⚽ Condición para el modelo: {clima['condicion']}")
            print()
        else:
            print(f"⚠️ No se pudo obtener clima para {equipo}\n")