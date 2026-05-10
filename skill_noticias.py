NOMBRES_BUSQUEDA = {
    "FC Barcelona": "Barcelona",
    "Real Madrid CF": "Real Madrid",
    "Manchester City FC": "Manchester City",
    "Liverpool FC": "Liverpool",
    "Arsenal FC": "Arsenal",
    "Chelsea FC": "Chelsea",
    "Manchester United FC": "Manchester United",
    "Tottenham Hotspur FC": "Tottenham",
    "Newcastle United FC": "Newcastle",
    "Aston Villa FC": "Aston Villa",
    "Bayern München": "Bayern Munich",
    "Paris Saint-Germain FC": "PSG",
    "Juventus FC": "Juventus",
    "Club Atlético de Madrid": "Atletico Madrid",
    "Inter Milan": "Inter Milan",
    "AC Milan": "AC Milan",
    "Borussia Dortmund": "Borussia Dortmund",
    "AFC Bournemouth": "Bournemouth",
    "Nottingham Forest FC": "Nottingham Forest",
    "Wolverhampton Wanderers FC": "Wolves",
    "Brighton & Hove Albion FC": "Brighton",
    "Brentford FC": "Brentford",
    "Fulham FC": "Fulham",
    "Everton FC": "Everton",
    "Crystal Palace FC": "Crystal Palace",
    "Sunderland AFC": "Sunderland",
    "Leeds United FC": "Leeds United",
    "Burnley FC": "Burnley",
    "RC Celta de Vigo": "Celta Vigo",
    "Sevilla FC": "Sevilla",
    "Valencia CF": "Valencia",
    "Real Betis Balompié": "Real Betis",
    "Getafe CF": "Getafe",
    "Deportivo Alavés": "Alaves",
    "Rayo Vallecano de Madrid": "Rayo Vallecano",
    "UD Las Palmas": "Las Palmas",
    "CA Osasuna": "Osasuna",
    "Girona FC": "Girona",
    "RCD Mallorca": "Mallorca",
    "RCD Espanyol de Barcelona": "Espanyol",
    "Real Sociedad de Fútbol": "Real Sociedad",
    "Athletic Club": "Athletic Bilbao",
    "Villarreal CF": "Villarreal",
    "AFC Ajax": "Ajax",
    "FC Porto": "Porto",
    "SL Benfica": "Benfica",
    "Sporting CP": "Sporting CP",
    "SSC Napoli": "Napoli",
    "RB Leipzig": "RB Leipzig",
    "FC Red Bull Salzburg": "Red Bull Salzburg",
}

def obtener_links_noticias(equipo):
    nombre = NOMBRES_BUSQUEDA.get(equipo, equipo.replace(" FC", "").replace(" CF", ""))
    query = nombre.replace(" ", "+")

    links = {
        "equipo": equipo,
        "nombre_busqueda": nombre,
        "urls": {
            "BBC Sport": f"https://www.bbc.com/sport/football?search={query}",
            "ESPN": f"https://www.espn.com/soccer/search/_/q/{query}",
            "Transfermarkt": f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}",
            "Google Noticias": f"https://news.google.com/search?q={query}+injury+lesion+baja&hl=es",
            "SofaScore": f"https://www.sofascore.com/search/{query}",
        },
        "factor_ajuste": 1.0,
        "lesiones_graves": [],
        "lesiones_moderadas": [],
        "lesiones_leves": [],
        "resumen": "Consulta los links para ver novedades"
    }
    return links

def buscar_noticias_equipo(equipo):
    return obtener_links_noticias(equipo)

if __name__ == "__main__":
    info = buscar_noticias_equipo("Arsenal FC")
    print(f"🏟️ {info['equipo']}")
    print(f"🔍 Links de noticias:")
    for nombre, url in info["urls"].items():
        print(f"  → {nombre}: {url}")