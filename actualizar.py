import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle
import os
from datetime import datetime

print("="*50)
print(f"🤖 ACTUALIZACIÓN AUTOMÁTICA")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*50)

# ── PASO 1: Descargar datos nuevos ──────────────────
print("\n📥 PASO 1: Descargando partidos nuevos...")

API_KEY = "6995e5f307174fc7909a551bf2394bf0"  # ← tu clave
headers = {"X-Auth-Token": API_KEY}

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
        print(f"  ⚠️ Sin datos para {liga_codigo} {temporada}: {datos.get('message', '')}")
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

todos = []
for codigo, nombre in LIGAS.items():
    for temporada in [2022, 2023, 2024]:
        print(f"  → Descargando {nombre} {temporada}...")
        todos += obtener_partidos(codigo, temporada)

df = pd.DataFrame(todos)
df.to_csv("partidos.csv", index=False)
print(f"  ✅ {len(df)} partidos guardados")

# ── PASO 2: Entrenar modelos ────────────────────────
print("\n🤖 PASO 2: Entrenando modelos por liga...")

equipos = list(set(df["local"].unique()) | set(df["visitante"].unique()))
equipo_id = {equipo: i for i, equipo in enumerate(equipos)}
df["local_id"] = df["local"].map(equipo_id)
df["visitante_id"] = df["visitante"].map(equipo_id)

def calcular_stats(df):
    df = df.copy().reset_index(drop=True)
    for col in ["forma_local", "forma_visitante",
                "goles_favor_local", "goles_contra_local",
                "goles_favor_visitante", "goles_contra_visitante",
                "victorias_local", "victorias_visitante",
                "empates_local", "empates_visitante",
                "racha_local", "racha_visitante"]:
        df[col] = 0.0
    for i, row in df.iterrows():
        pl = df[(df["local"] == row["local"]) & (df.index < i)].tail(7)
        pv = df[(df["visitante"] == row["visitante"]) & (df.index < i)].tail(7)
        if len(pl) > 0:
            df.at[i, "forma_local"] = pl["goles_local"].mean()
            df.at[i, "goles_favor_local"] = pl["goles_local"].mean()
            df.at[i, "goles_contra_local"] = pl["goles_visitante"].mean()
            df.at[i, "victorias_local"] = (pl["resultado"] == "L").mean()
            df.at[i, "empates_local"] = (pl["resultado"] == "E").mean()
            df.at[i, "racha_local"] = pl["goles_local"].sum() - pl["goles_visitante"].sum()
        if len(pv) > 0:
            df.at[i, "forma_visitante"] = pv["goles_visitante"].mean()
            df.at[i, "goles_favor_visitante"] = pv["goles_visitante"].mean()
            df.at[i, "goles_contra_visitante"] = pv["goles_local"].mean()
            df.at[i, "victorias_visitante"] = (pv["resultado"] == "V").mean()
            df.at[i, "empates_visitante"] = (pv["resultado"] == "E").mean()
            df.at[i, "racha_visitante"] = pv["goles_visitante"].sum() - pv["goles_local"].sum()
    return df

FEATURES = [
    "local_id", "visitante_id",
    "forma_local", "forma_visitante",
    "goles_favor_local", "goles_contra_local",
    "goles_favor_visitante", "goles_contra_visitante",
    "victorias_local", "victorias_visitante",
    "empates_local", "empates_visitante",
    "racha_local", "racha_visitante"
]

modelos_por_liga = {}
for liga in df["liga"].unique():
    print(f"  → Entrenando {liga}...")
    df_liga = df[df["liga"] == liga].copy()
    df_liga = calcular_stats(df_liga)
    X = df_liga[FEATURES]
    y = df_liga["resultado"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42)
    modelo.fit(X_train, y_train)
    precision = accuracy_score(y_test, modelo.predict(X_test))
    print(f"     🎯 Precisión: {precision*100:.1f}%")
    modelos_por_liga[liga] = modelo

pickle.dump(modelos_por_liga, open("modelo.pkl", "wb"))
pickle.dump(equipo_id, open("equipos.pkl", "wb"))
print("  ✅ Modelos guardados")

# ── PASO 3: Subir a GitHub ──────────────────────────
print("\n📤 PASO 3: Subiendo cambios a GitHub...")
os.system('git add .')
os.system('git commit -m "actualizacion automatica de datos y modelo"')
os.system('git push')
print("  ✅ Cambios subidos a GitHub")

print("\n" + "="*50)
print("🎉 ACTUALIZACIÓN COMPLETA")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*50)