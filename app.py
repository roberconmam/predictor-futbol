import streamlit as st
import pickle
import numpy as np
import pandas as pd
from scipy.stats import poisson

modelos_por_liga = pickle.load(open("modelo.pkl", "rb"))
equipo_id = pickle.load(open("equipos.pkl", "rb"))
df_partidos = pd.read_csv("partidos.csv")

ligas = {
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {
        "key": "Premier League", "precision": 49.3,
        "equipos": [
            "Arsenal FC", "Chelsea FC", "Liverpool FC", "Manchester City FC",
            "Manchester United FC", "Tottenham Hotspur FC", "Newcastle United FC",
            "Aston Villa FC", "Brighton & Hove Albion FC", "West Ham United FC",
            "Brentford FC", "Fulham FC", "Everton FC", "AFC Bournemouth",
            "Nottingham Forest FC", "Wolverhampton Wanderers FC", "Crystal Palace FC",
            "Sunderland AFC", "Leeds United FC", "Burnley FC"
        ]
    },
    "🇪🇸 La Liga": {
        "key": "La Liga", "precision": 43.4,
        "equipos": [
            "FC Barcelona", "Real Madrid CF", "Club Atlético de Madrid",
            "Real Sociedad de Fútbol", "Athletic Club", "Villarreal CF",
            "RC Celta de Vigo", "Sevilla FC", "Valencia CF", "Real Betis Balompié",
            "Getafe CF", "Deportivo Alavés", "Rayo Vallecano de Madrid",
            "UD Las Palmas", "CA Osasuna", "Girona FC", "RCD Mallorca",
            "RCD Espanyol de Barcelona", "Elche CF", "Cádiz CF"
        ]
    },
    "🇪🇺 Champions League": {
        "key": "Champions League", "precision": 50.8,
        "equipos": [
            "FC Barcelona", "Real Madrid CF", "Manchester City FC", "Liverpool FC",
            "Bayern München", "Paris Saint-Germain FC", "Juventus FC", "Chelsea FC",
            "Borussia Dortmund", "Club Atlético de Madrid", "Arsenal FC",
            "Inter Milan", "AC Milan", "AFC Ajax", "FC Porto",
            "SL Benfica", "Sporting CP", "SSC Napoli", "RB Leipzig", "FC Red Bull Salzburg"
        ]
    }
}

def calcular_lambda(equipo_local, equipo_visitante, liga_key):
    df = df_partidos[df_partidos["liga"] == liga_key].copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha")
    promedio_goles_liga = df["goles_local"].mean()

    partidos_local = df[df["local"] == equipo_local].tail(10)
    partidos_visit = df[df["visitante"] == equipo_visitante].tail(10)
    if len(partidos_local) < 3:
        partidos_local = df[df["local"] == equipo_local]
    if len(partidos_visit) < 3:
        partidos_visit = df[df["visitante"] == equipo_visitante]

    hist_local = df[df["local"] == equipo_local]
    hist_visit = df[df["visitante"] == equipo_visitante]

    def safe_mean(series, fallback=1.0):
        return series.mean() if len(series) > 0 else fallback

    ataque_local = (0.7 * safe_mean(partidos_local["goles_local"]) + 0.3 * safe_mean(hist_local["goles_local"])) / promedio_goles_liga
    defensa_local = (0.7 * safe_mean(partidos_local["goles_visitante"]) + 0.3 * safe_mean(hist_local["goles_visitante"])) / promedio_goles_liga
    ataque_visit = (0.7 * safe_mean(partidos_visit["goles_visitante"]) + 0.3 * safe_mean(hist_visit["goles_visitante"])) / promedio_goles_liga
    defensa_visit = (0.7 * safe_mean(partidos_visit["goles_local"]) + 0.3 * safe_mean(hist_visit["goles_local"])) / promedio_goles_liga

    lambda_local = ataque_local * defensa_visit * promedio_goles_liga * 1.1
    lambda_visit = ataque_visit * defensa_local * promedio_goles_liga

    return round(lambda_local, 2), round(lambda_visit, 2)

def calcular_todo(lambda_local, lambda_visit, max_goles=6):
    # Matriz de probabilidades de marcadores
    matriz = np.zeros((max_goles+1, max_goles+1))
    for i in range(max_goles+1):
        for j in range(max_goles+1):
            matriz[i][j] = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visit)

    # Probabilidades de resultado desde la misma matriz
    prob_local = np.sum(np.tril(matriz, -1))    # goles_local > goles_visit
    prob_empate = np.sum(np.diag(matriz))        # goles_local == goles_visit
    prob_visit = np.sum(np.triu(matriz, 1))      # goles_visit > goles_local

    return matriz, prob_local, prob_empate, prob_visit

# UI
st.set_page_config(page_title="Predictor de Fútbol", page_icon="⚽", layout="centered")
st.markdown("""
<style>
.titulo { text-align: center; font-size: 2.5em; font-weight: bold; color: #38003c; }
.subtitulo { text-align: center; color: gray; margin-bottom: 20px; }
.resultado { text-align: center; font-size: 1.8em; font-weight: bold; padding: 15px;
             border-radius: 10px; background-color: #38003c; color: white; }
.precision { text-align: center; font-size: 0.9em; color: #4CAF50; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">⚽ Predictor de Fútbol</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Premier League · La Liga · Champions League</div>', unsafe_allow_html=True)
st.divider()

liga_seleccionada = st.selectbox("🏆 Selecciona la Liga", list(ligas.keys()))
info_liga = ligas[liga_seleccionada]
equipos_liga = sorted([e for e in info_liga["equipos"] if e in equipo_id])

st.markdown(f'<div class="precision">🎯 Precisión del modelo: {info_liga["precision"]}%</div>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏠 Local")
    equipo_local = st.selectbox("", equipos_liga, key="local", label_visibility="collapsed")
with col2:
    st.markdown("### ✈️ Visitante")
    equipo_visitante = st.selectbox("", equipos_liga, index=1, key="visitante", label_visibility="collapsed")

st.divider()

tab1, tab2 = st.tabs(["🔮 Predecir Resultado", "⚽ Predecir Marcador"])

# Calculamos todo de una vez con Poisson
if equipo_local != equipo_visitante:
    lambda_l, lambda_v = calcular_lambda(equipo_local, equipo_visitante, info_liga["key"])
    matriz, prob_l, prob_e, prob_v = calcular_todo(lambda_l, lambda_v)

    with tab1:
        if st.button("🔮 Predecir Resultado", use_container_width=True, type="primary"):
            if prob_l > prob_v and prob_l > prob_e:
                ganador = f"🏆 Gana {equipo_local}"
            elif prob_v > prob_l and prob_v > prob_e:
                ganador = f"🏆 Gana {equipo_visitante}"
            else:
                ganador = "🤝 Empate"

            st.markdown(f'<div class="resultado">{ganador}</div>', unsafe_allow_html=True)
            st.divider()
            st.markdown("### 📊 Probabilidades")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"🏠 {equipo_local[:12]}", f"{prob_l*100:.1f}%")
                st.progress(float(prob_l))
            with col2:
                st.metric("🤝 Empate", f"{prob_e*100:.1f}%")
                st.progress(float(prob_e))
            with col3:
                st.metric(f"✈️ {equipo_visitante[:12]}", f"{prob_v*100:.1f}%")
                st.progress(float(prob_v))
            st.caption("⚠️ Predicción basada en modelo Poisson con estadísticas históricas.")

    with tab2:
        if st.button("⚽ Predecir Marcador", use_container_width=True, type="primary", key="btn_marcador"):
            idx = np.unravel_index(matriz.argmax(), matriz.shape)
            goles_l, goles_v = idx[0], idx[1]

            st.markdown(f"""
            <div style='text-align:center; background:#1a1a2e; padding:20px; border-radius:12px; margin-bottom:20px'>
                <div style='color:gray; font-size:0.9em'>Marcador más probable</div>
                <div style='font-size:3em; font-weight:bold; color:#4CAF50'>{goles_l} - {goles_v}</div>
                <div style='color:gray'>{equipo_local} vs {equipo_visitante}</div>
                <div style='color:#4CAF50'>Probabilidad: {matriz[goles_l][goles_v]*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"⚽ Goles esperados {equipo_local[:10]}", f"{lambda_l:.2f}")
            with col2:
                st.metric(f"⚽ Goles esperados {equipo_visitante[:10]}", f"{lambda_v:.2f}")

            st.divider()

            # Consistencia con resultado
            st.markdown("### 🔗 Consistencia con resultado")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"🏠 {equipo_local[:12]}", f"{prob_l*100:.1f}%")
                st.progress(float(prob_l))
            with col2:
                st.metric("🤝 Empate", f"{prob_e*100:.1f}%")
                st.progress(float(prob_e))
            with col3:
                st.metric(f"✈️ {equipo_visitante[:12]}", f"{prob_v*100:.1f}%")
                st.progress(float(prob_v))

            st.divider()
            st.subheader("🏆 Top 5 Marcadores más probables")
            resultados = [{"Marcador": f"{i} - {j}", "Probabilidad": f"{matriz[i][j]*100:.1f}%",
                           "prob_num": matriz[i][j]} for i in range(7) for j in range(7)]
            top5 = sorted(resultados, key=lambda x: x["prob_num"], reverse=True)[:5]
            for k, r in enumerate(top5):
                medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                st.markdown(f"{medallas[k]} **{r['Marcador']}** — {r['Probabilidad']}")

            st.caption("⚠️ Basado en modelo de Poisson con estadísticas históricas.")
else:
    with tab1:
        st.warning("⚠️ Elige dos equipos diferentes")
    with tab2:
        st.warning("⚠️ Elige dos equipos diferentes")