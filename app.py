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

# Factores de ajuste
AJUSTES_BAJAS = {"Ninguna baja": 1.0, "1 titular fuera": 0.90, "2+ titulares fuera": 0.78}
AJUSTES_DESCANSO = {"7+ días": 1.05, "4-6 días": 1.0, "1-3 días": 0.90}
AJUSTES_ANIMO = {"Muy bien 🔥": 1.10, "Normal": 1.0, "Mal 😞": 0.88}
AJUSTES_IMPORTANCIA = {"Final / Derby": 0.92, "Partido importante": 0.96, "Normal": 1.0}
AJUSTES_CLIMA = {"Bueno ☀️": 1.0, "Lluvia 🌧️": 0.93, "Viento fuerte 💨": 0.95}
AJUSTES_ESTADIO = {"Estadio lleno 🏟️": 1.08, "Medio lleno": 1.03, "Vacío": 0.97}

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

def aplicar_ajustes(lambda_l, lambda_v, ajustes):
    # Ajustes al local
    lambda_l *= ajustes["bajas_local"]
    lambda_l *= ajustes["descanso_local"]
    lambda_l *= ajustes["animo_local"]
    lambda_l *= ajustes["estadio"]
    lambda_l *= ajustes["importancia"]
    lambda_l *= ajustes["clima"]

    # Ajustes al visitante
    lambda_v *= ajustes["bajas_visit"]
    lambda_v *= ajustes["descanso_visit"]
    lambda_v *= ajustes["animo_visit"]
    lambda_v *= ajustes["importancia"]
    lambda_v *= ajustes["clima"]

    return round(lambda_l, 2), round(lambda_v, 2)

def calcular_todo(lambda_local, lambda_visit, max_goles=6):
    matriz = np.zeros((max_goles+1, max_goles+1))
    for i in range(max_goles+1):
        for j in range(max_goles+1):
            matriz[i][j] = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visit)
    prob_local = np.sum(np.tril(matriz, -1))
    prob_empate = np.sum(np.diag(matriz))
    prob_visit = np.sum(np.triu(matriz, 1))
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
.ajuste-box { background: #1a1a2e; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">⚽ Predictor de Fútbol</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Premier League · La Liga · Champions League</div>', unsafe_allow_html=True)
st.divider()

liga_seleccionada = st.selectbox("🏆 Selecciona la Liga", list(ligas.keys()))
info_liga = ligas[liga_seleccionada]
equipos_liga = sorted([e for e in info_liga["equipos"] if e in equipo_id])
st.markdown(f'<div class="precision">🎯 Precisión base del modelo: {info_liga["precision"]}%</div>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏠 Local")
    equipo_local = st.selectbox("", equipos_liga, key="local", label_visibility="collapsed")
with col2:
    st.markdown("### ✈️ Visitante")
    equipo_visitante = st.selectbox("", equipos_liga, index=1, key="visitante", label_visibility="collapsed")

st.divider()

# Variables manuales
with st.expander("⚙️ Ajustes del partido (opcional)", expanded=False):
    st.markdown("#### 🏠 Equipo Local")
    col1, col2, col3 = st.columns(3)
    with col1:
        bajas_local = st.selectbox("🤕 Bajas", list(AJUSTES_BAJAS.keys()), key="bl")
    with col2:
        descanso_local = st.selectbox("📅 Descanso", list(AJUSTES_DESCANSO.keys()), key="dl")
    with col3:
        animo_local = st.selectbox("📈 Ánimo", list(AJUSTES_ANIMO.keys()), key="al")

    st.markdown("#### ✈️ Equipo Visitante")
    col1, col2, col3 = st.columns(3)
    with col1:
        bajas_visit = st.selectbox("🤕 Bajas", list(AJUSTES_BAJAS.keys()), key="bv")
    with col2:
        descanso_visit = st.selectbox("📅 Descanso", list(AJUSTES_DESCANSO.keys()), key="dv")
    with col3:
        animo_visit = st.selectbox("📈 Ánimo", list(AJUSTES_ANIMO.keys()), key="av")

    st.markdown("#### 🌍 Condiciones del Partido")
    col1, col2, col3 = st.columns(3)
    with col1:
        clima = st.selectbox("🌤️ Clima", list(AJUSTES_CLIMA.keys()), key="cl")
    with col2:
        estadio = st.selectbox("🏟️ Estadio", list(AJUSTES_ESTADIO.keys()), key="est")
    with col3:
        importancia = st.selectbox("🏆 Importancia", list(AJUSTES_IMPORTANCIA.keys()), key="imp")

st.divider()

tab1, tab2 = st.tabs(["🔮 Predecir Resultado", "⚽ Predecir Marcador"])

if equipo_local != equipo_visitante:
    lambda_l, lambda_v = calcular_lambda(equipo_local, equipo_visitante, info_liga["key"])

    # Aplicamos ajustes manuales
    ajustes = {
        "bajas_local": AJUSTES_BAJAS[bajas_local],
        "descanso_local": AJUSTES_DESCANSO[descanso_local],
        "animo_local": AJUSTES_ANIMO[animo_local],
        "bajas_visit": AJUSTES_BAJAS[bajas_visit],
        "descanso_visit": AJUSTES_DESCANSO[descanso_visit],
        "animo_visit": AJUSTES_ANIMO[animo_visit],
        "clima": AJUSTES_CLIMA[clima],
        "estadio": AJUSTES_ESTADIO[estadio],
        "importancia": AJUSTES_IMPORTANCIA[importancia],
    }
    lambda_l_aj, lambda_v_aj = aplicar_ajustes(lambda_l, lambda_v, ajustes)
    matriz, prob_l, prob_e, prob_v = calcular_todo(lambda_l_aj, lambda_v_aj)

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

            # Mostramos si hubo ajustes
            if any(v != 1.0 for v in ajustes.values()):
                st.info(f"⚙️ Goles base: {lambda_l:.2f} vs {lambda_v:.2f} → Ajustados: {lambda_l_aj:.2f} vs {lambda_v_aj:.2f}")
            st.caption("⚠️ Predicción basada en modelo Poisson con ajustes manuales.")

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
                st.metric(f"⚽ Goles esperados {equipo_local[:10]}", f"{lambda_l_aj:.2f}")
            with col2:
                st.metric(f"⚽ Goles esperados {equipo_visitante[:10]}", f"{lambda_v_aj:.2f}")

            if any(v != 1.0 for v in ajustes.values()):
                st.info(f"⚙️ Sin ajustes: {lambda_l:.2f} vs {lambda_v:.2f} → Con ajustes: {lambda_l_aj:.2f} vs {lambda_v_aj:.2f}")

            st.divider()
            st.markdown("### 🔗 Probabilidades de resultado")
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
            st.caption("⚠️ Basado en modelo Poisson con ajustes manuales.")
else:
    with tab1:
        st.warning("⚠️ Elige dos equipos diferentes")
    with tab2:
        st.warning("⚠️ Elige dos equipos diferentes")