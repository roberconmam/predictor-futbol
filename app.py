import streamlit as st
import pickle
import numpy as np

modelo = pickle.load(open("modelo.pkl", "rb"))
equipo_id = pickle.load(open("equipos.pkl", "rb"))

# Separamos equipos por liga
ligas = {
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": [
        "Arsenal FC", "Chelsea FC", "Liverpool FC", "Manchester City FC",
        "Manchester United FC", "Tottenham Hotspur FC", "Newcastle United FC",
        "Aston Villa FC", "Brighton & Hove Albion FC", "West Ham United FC",
        "Brentford FC", "Fulham FC", "Everton FC", "AFC Bournemouth",
        "Nottingham Forest FC", "Wolverhampton Wanderers FC", "Crystal Palace FC",
        "Sunderland AFC", "Leeds United FC", "Burnley FC"
    ],
    "🇪🇸 La Liga": [
        "FC Barcelona", "Real Madrid CF", "Club Atlético de Madrid",
        "Real Sociedad de Fútbol", "Athletic Club", "Villarreal CF",
        "RC Celta de Vigo", "Sevilla FC", "Valencia CF", "Real Betis Balompié",
        "Getafe CF", "Deportivo Alavés", "Rayo Vallecano de Madrid",
        "UD Las Palmas", "CA Osasuna", "Girona FC", "RCD Mallorca",
        "RCD Espanyol de Barcelona", "Elche CF", "Cádiz CF"
    ],
    "🇪🇺 Champions League": [
        "FC Barcelona", "Real Madrid CF", "Manchester City FC", "Liverpool FC",
        "Bayern München", "Paris Saint-Germain FC", "Juventus FC", "Chelsea FC",
        "Borussia Dortmund", "Club Atlético de Madrid", "Arsenal FC",
        "Inter Milan", "AC Milan", "AFC Ajax", "FC Porto",
        "SL Benfica", "Sporting CP", "SSC Napoli", "RB Leipzig", "FC Red Bull Salzburg"
    ]
}

st.set_page_config(page_title="Predictor de Fútbol", page_icon="⚽", layout="centered")

st.markdown("""
<style>
.titulo { text-align: center; font-size: 2.5em; font-weight: bold; color: #38003c; }
.subtitulo { text-align: center; color: gray; margin-bottom: 20px; }
.resultado { text-align: center; font-size: 1.8em; font-weight: bold; padding: 15px;
             border-radius: 10px; background-color: #38003c; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">⚽ Predictor de Fútbol</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Premier League · La Liga · Champions League</div>', unsafe_allow_html=True)
st.divider()

# Selector de liga
liga_seleccionada = st.selectbox("🏆 Selecciona la Liga", list(ligas.keys()))
equipos_liga = sorted([e for e in ligas[liga_seleccionada] if e in equipo_id])

if len(equipos_liga) < 2:
    st.warning("⚠️ Pocos equipos disponibles para esta liga en el modelo.")
else:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏠 Local")
        equipo_local = st.selectbox("", equipos_liga, key="local", label_visibility="collapsed")
    with col2:
        st.markdown("### ✈️ Visitante")
        equipo_visitante = st.selectbox("", equipos_liga, index=1, key="visitante", label_visibility="collapsed")

    st.divider()

    if st.button("🔮 Predecir Resultado", use_container_width=True, type="primary"):
        if equipo_local == equipo_visitante:
            st.warning("⚠️ Elige dos equipos diferentes")
        else:
            local_id = equipo_id[equipo_local]
            visitante_id = equipo_id[equipo_visitante]
            X = np.array([[local_id, visitante_id, 1.5, 1.2, 1.5, 1.0, 1.2, 1.0, 0.5, 0.4]])

            probs = modelo.predict_proba(X)[0]
            clases = modelo.classes_
            prob_dict = dict(zip(clases, probs))

            prob_local = prob_dict.get("L", 0)
            prob_empate = prob_dict.get("E", 0)
            prob_visitante = prob_dict.get("V", 0)

            resultado = max(prob_dict, key=prob_dict.get)
            if resultado == "L":
                ganador = f"🏆 Gana {equipo_local}"
            elif resultado == "V":
                ganador = f"🏆 Gana {equipo_visitante}"
            else:
                ganador = "🤝 Empate"

            st.markdown(f'<div class="resultado">{ganador}</div>', unsafe_allow_html=True)
            st.divider()

            st.markdown("### 📊 Probabilidades")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"🏠 {equipo_local[:12]}", f"{prob_local*100:.1f}%")
                st.progress(float(prob_local))
            with col2:
                st.metric("🤝 Empate", f"{prob_empate*100:.1f}%")
                st.progress(float(prob_empate))
            with col3:
                st.metric(f"✈️ {equipo_visitante[:12]}", f"{prob_visitante*100:.1f}%")
                st.progress(float(prob_visitante))

            st.divider()
            st.caption("⚠️ Esta predicción es orientativa. El fútbol siempre sorprende.")