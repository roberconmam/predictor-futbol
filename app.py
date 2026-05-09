import streamlit as st
import pickle
import numpy as np

modelo = pickle.load(open("modelo.pkl", "rb"))
equipo_id = pickle.load(open("equipos.pkl", "rb"))
equipos = sorted(equipo_id.keys())

st.set_page_config(page_title="Predictor de Fútbol", page_icon="⚽", layout="centered")

# Estilo
st.markdown("""
<style>
.titulo { text-align: center; font-size: 2.5em; font-weight: bold; color: #38003c; }
.subtitulo { text-align: center; color: gray; margin-bottom: 20px; }
.resultado { text-align: center; font-size: 1.8em; font-weight: bold; padding: 15px;
             border-radius: 10px; background-color: #38003c; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">⚽ Predictor Premier League</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Powered by Machine Learning · 52% de precisión</div>', unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏠 Local")
    equipo_local = st.selectbox("", equipos, key="local", label_visibility="collapsed")
with col2:
    st.markdown("### ✈️ Visitante")
    equipo_visitante = st.selectbox("", equipos, index=1, key="visitante", label_visibility="collapsed")

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