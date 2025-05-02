import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

st.title("👥 Participantes - Porra Futbolera")

# Leer resultados y supervivientes
try:
    with open("data/resultados.json", "r") as f:
        datos = json.load(f)
    partidos = datos["partidos"]
    resultados = datos["resultados"]

    st.subheader("📋 Partidos de la jornada")
    st.markdown(f"**⚽ {partidos['Real Madrid']}** → Resultado: `{resultados['Real Madrid']}`")
    st.markdown(f"**⚽ {partidos['Barcelona']}** → Resultado: `{resultados['Barcelona']}`")
    st.markdown(f"**⚽ {partidos['Ponferradina']}** → Resultado: `{resultados['Ponferradina']}`")

    if os.path.exists("data/supervivientes.csv"):
        df = pd.read_csv("data/supervivientes.csv")

        st.subheader("🟢 Participantes que siguen vivos")

        if df.empty:
            st.error("😢 Ningún participante acertó los tres partidos.")
        else:
            st.success(f"🎉 ¡Quedan {len(df)} participantes en juego!")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no se han publicado resultados.")

except Exception as e:
    st.error("❌ No se pudieron cargar los datos. Asegúrate de que el encargado haya publicado los resultados.")
