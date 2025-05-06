import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        button[kind="header"] {display: none !important;}
        .st-emotion-cache-zq5wmm, .st-emotion-cache-1avcm0n, .css-1lsmgbg, .css-eczf16 {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Diccionario de nombres y rutas de escudos personalizados
# Asegúrate de que las claves coincidan con los slugs de tu JSON de partidos
custom_teams = {
    # Primera División
    "futbol-club-barcelona": ("Barcelona", "logos/barcelona.png"),
    "real-madrid-club-de-futbol": ("Real Madrid", "logos/real_madrid.png"),
    "club-atletico-de-madrid": ("Atlético", "logos/atletico.png"),
    "athletic-club": ("Athletic", "logos/athletic.png"),
    "villarreal-cf": ("Villarreal", "logos/villarreal.png"),
    "real-betis-balompie": ("Betis", "logos/betis.png"),
    "real-club-deportivo-celta-de-vigo": ("Celta", "logos/celta.png"),
    "rayo-vallecano-de-madrid": ("Rayo", "logos/rayo.png"),
    "club-atletico-osasuna": ("Osasuna", "logos/osasuna.png"),
    "real-club-deportivo-mallorca": ("Mallorca", "logos/mallorca.png"),
    "real-sociedad-de-futbol": ("R. Sociedad", "logos/real_sociedad.png"),
    "valencia-cf": ("Valencia", "logos/valencia.png"),
    "getafe-cf": ("Getafe", "logos/getafe.png"),
    "reial-club-deportiu-espanyol": ("Espanyol", "logos/espanyol.png"),
    "girona-fc": ("Girona", "logos/girona.png"),
    "sevilla-fc": ("Sevilla", "logos/sevilla.png"),
    "deportivo-alaves": ("Alavés", "logos/alaves.png"),
    "union-deportiva-las-palmas": ("Las Palmas", "logos/las_palmas.png"),
    "club-deportivo-leganes": ("Leganés", "logos/leganes.png"),
    "real-valladolid-cf": ("Real Valladolid", "logos/real_valladolid.png"),
    # Primera Federación (Tercer partido)
    "cultural-y-deportiva-leonesa": ("Cultural", "logos/cultural.png"),
    "ponferradina": ("Ponferradina", "logos/ponferradina.png"),
    "fc-andorra": ("Andorra", "logos/andorra.png"),
    "real-sociedad-b": ("R. Sociedad B", "logos/real_sociedad_b.png"),
    "gimnastic-de-tarragona": ("Gimnàstic", "logos/gimnastic.png"),
    "bilbao-athletic": ("Bilbao Athletic", "logos/bilbao_athletic.png"),
    "celta-de-vigo-b": ("Celta B", "logos/celta_b.png"),
    "ourense-cf": ("Ourense CF", "logos/ourense.png"),
    "zamora-cf": ("Zamora", "logos/zamora.png"),
    "barakaldo-cf": ("Barakaldo", "logos/barakaldo.png"),
    "club-deportivo-arenteiro": ("CD Arenteiro", "logos/arenteiro.png"),
    "cd-tarazona": ("Tarazona", "logos/tarazona.png"),
    "real-union": ("Real Unión", "logos/real_union.png"),
    "cd-lugo": ("Lugo", "logos/lugo.png"),
    "unionistas-cf": ("Unionistas CF", "logos/unionistas.png"),
    "sestao-river": ("Sestao", "logos/sestao.png"),
    "osasuna-b": ("Osasuna B", "logos/osasuna_b.png"),
    "fc-barcelona-b": ("Barcelona B", "logos/barcelona_b.png"),
    "gimnastic-segoviana": ("G. Segoviana", "logos/segoviana.png"),
    "sd-amorebieta": ("SD Amorebieta", "logos/amorebieta.png")
}

# Leer resultados y supervivientes
try:
    with open("data/resultados.json", "r") as f:
        datos = json.load(f)
    partidos = datos["partidos"]  # debe incluir entradas para los tres partidos
    resultados = datos["resultados"]

    st.subheader("📋 Partidos de la jornada")
    # Recorremos todos los partidos, filtramos por custom_teams
    for key, slug in partidos.items():
        if slug not in custom_teams:
            continue
        display_name, logo_path = custom_teams[slug]
        marcador = resultados.get(key, "")
        # Mostrar escudo y nombre
        if os.path.exists(logo_path):
            st.image(logo_path, width=30, caption=display_name)
        else:
            st.write(f"⚽ **{display_name}**")
        # Mostrar resultado en verde, tamaño duplicado
        st.markdown(
            f"<span style='font-size:2em; color:green;'>{marcador}</span>",
            unsafe_allow_html=True
        )

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

except Exception:
    st.error("❌ No se pudieron cargar los datos. Asegúrate de que el encargado haya publicado los resultados.")
