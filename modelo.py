import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

df = pd.read_csv("partidos.csv")
print(f"✅ {len(df)} partidos cargados")

# IDs de equipos globales
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

# Entrenamos un modelo por liga
modelos_por_liga = {}
ligas = df["liga"].unique()

for liga in ligas:
    print(f"\n🏆 Entrenando modelo para {liga}...")
    df_liga = df[df["liga"] == liga].copy()
    df_liga = calcular_stats(df_liga)

    X = df_liga[FEATURES]
    y = df_liga["resultado"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42)
    modelo.fit(X_train, y_train)

    precision = accuracy_score(y_test, modelo.predict(X_test))
    print(f"   🎯 Precisión {liga}: {precision*100:.1f}%")

    modelos_por_liga[liga] = modelo

# Guardamos todo
pickle.dump(modelos_por_liga, open("modelo.pkl", "wb"))
pickle.dump(equipo_id, open("equipos.pkl", "wb"))
print("\n✅ Modelos por liga guardados!")