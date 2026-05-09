import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

df = pd.read_csv("partidos.csv")
print(f"✅ {len(df)} partidos cargados")

# IDs de equipos
equipos = list(set(df["local"].unique()) | set(df["visitante"].unique()))
equipo_id = {equipo: i for i, equipo in enumerate(equipos)}
df["local_id"] = df["local"].map(equipo_id)
df["visitante_id"] = df["visitante"].map(equipo_id)

# Variables nuevas mejoradas
def calcular_stats(df):
    df = df.copy()
    df["forma_local"] = 0.0
    df["forma_visitante"] = 0.0
    df["goles_favor_local"] = 0.0
    df["goles_contra_local"] = 0.0
    df["goles_favor_visitante"] = 0.0
    df["goles_contra_visitante"] = 0.0
    df["victorias_local"] = 0.0
    df["victorias_visitante"] = 0.0

    for i, row in df.iterrows():
        # Últimos 5 partidos del local
        pl = df[(df["local"] == row["local"]) & (df.index < i)].tail(5)
        pv = df[(df["visitante"] == row["visitante"]) & (df.index < i)].tail(5)

        if len(pl) > 0:
            df.at[i, "forma_local"] = pl["goles_local"].mean()
            df.at[i, "goles_favor_local"] = pl["goles_local"].mean()
            df.at[i, "goles_contra_local"] = pl["goles_visitante"].mean()
            df.at[i, "victorias_local"] = (pl["resultado"] == "L").mean()

        if len(pv) > 0:
            df.at[i, "forma_visitante"] = pv["goles_visitante"].mean()
            df.at[i, "goles_favor_visitante"] = pv["goles_visitante"].mean()
            df.at[i, "goles_contra_visitante"] = pv["goles_local"].mean()
            df.at[i, "victorias_visitante"] = (pv["resultado"] == "V").mean()

    return df

print("Calculando estadísticas mejoradas...")
df = calcular_stats(df)

# Más variables
X = df[[
    "local_id", "visitante_id",
    "forma_local", "forma_visitante",
    "goles_favor_local", "goles_contra_local",
    "goles_favor_visitante", "goles_contra_visitante",
    "victorias_local", "victorias_visitante"
]]
y = df["resultado"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Entrenando modelo mejorado...")
modelo = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
modelo.fit(X_train, y_train)

predicciones = modelo.predict(X_test)
precision = accuracy_score(y_test, predicciones)
print(f"\n🎯 Precisión del modelo mejorado: {precision*100:.1f}%")

pickle.dump(modelo, open("modelo.pkl", "wb"))
pickle.dump(equipo_id, open("equipos.pkl", "wb"))
print("✅ Modelo mejorado guardado!")