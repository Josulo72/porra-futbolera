import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import subprocess

st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

st.title("⚽ Panel del Encargado - Porra Futbolera")

# Equipos de La Liga EA Sports
equipos_laliga = [
    "Barcelona", "Real Madrid", "Atlético", "Athletic", "Villarreal",
    "Betis", "Celta", "Osasuna", "Mallorca", "R. Sociedad",
    "Rayo", "Getafe", "Espanyol", "Valencia", "Sevilla",
    "Girona", "Alavés", "Las Palmas", "Leganés", "Real Valladolid"
]

# Equipos de Primera Federación - Grupo 1
equipos_primera_federacion = [
    "Cultural Leonesa", "Ponferradina", "Gimnàstic", "Real Sociedad B", "Andorra",
    "Bilbao Athletic", "Zamora", "Celta B", "Tarazona", "Ourense CF",
    "Barakaldo", "CD Arenteiro", "Lugo", "Sestao", "Unionistas CF",
    "Osasuna B", "Real Unión", "Barcelona B", "Gimnástica Segoviana", "SD Amorebieta"
]

st.subheader("Selecciona los equipos y horarios de cada partido")

# Botón para ejecutar auto_resultados.py
auto_btn = st.button("🛰️ Consultar resultados automáticamente ahora")
if auto_btn:
    with st.spinner("Consultando resultados desde la API..."):
        result = subprocess.run(["python", "auto_resultados.py"], capture_output=True, text=True)
        st.code(result.stdout)
        if result.stderr:
            st.error("❌ Error al ejecutar el script:")
            st.code(result.stderr)
        else:
            st.success("✅ Consulta completada.")

# Partido 1: Real Madrid
col1, col2 = st.columns(2)
with col1:
    rm_local = st.selectbox("Equipo LOCAL (RM)", equipos_laliga, index=equipos_laliga.index("Real Madrid"))
with col2:
    rm_visitante = st.selectbox("Equipo VISITANTE (RM)", equipos_laliga, index=0)
fecha_rm = st.date_input("📅 Fecha del partido (RM)", value=datetime.today())
hora_rm = st.time_input("🕙 Hora estimada de finalización (RM)", value=datetime.strptime("23:00", "%H:%M").time())

# Partido 2: Barcelona
col3, col4 = st.columns(2)
with col3:
    bar_local = st.selectbox("Equipo LOCAL (BAR)", equipos_laliga, index=equipos_laliga.index("Barcelona"))
with col4:
    bar_visitante = st.selectbox("Equipo VISITANTE (BAR)", equipos_laliga, index=1)
fecha_bar = st.date_input("📅 Fecha del partido (BAR)", value=datetime.today())
hora_bar = st.time_input("🕙 Hora estimada de finalización (BAR)", value=datetime.strptime("21:45", "%H:%M").time())

# Partido 3: Ponferradina
col5, col6 = st.columns(2)
with col5:
    pon_local = st.selectbox("Equipo LOCAL (Ponfe)", equipos_primera_federacion, index=equipos_primera_federacion.index("Ponferradina"))
with col6:
    pon_visitante = st.selectbox("Equipo VISITANTE (Ponfe)", equipos_primera_federacion, index=1)
fecha_ponfe = st.date_input("📅 Fecha del partido (Ponfe)", value=datetime.today())
hora_ponfe = st.time_input("🕙 Hora estimada de finalización (Ponfe)", value=datetime.strptime("20:00", "%H:%M").time())

# Subida del Excel
st.subheader("📄 Sube el archivo Excel con las predicciones")
archivo_excel = st.file_uploader("Selecciona el archivo Excel", type=["xlsx"])

if archivo_excel:
    try:
        df = pd.read_excel(archivo_excel)
        st.success("✅ Archivo cargado correctamente.")
        st.write("🔍 Vista previa de las predicciones:")
        st.dataframe(df.astype(str))

        st.subheader("✍️ Introduce los resultados reales")
        resultado_rm = st.selectbox(f"Resultado {rm_local} vs {rm_visitante}", ["", "0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "3-0", "0-3", "3-1", "1-3", "3-2", "2-3", "3-3"])
        resultado_bar = st.selectbox(f"Resultado {bar_local} vs {bar_visitante}", ["", "0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2", "2-2", "3-0", "0-3", "3-1", "1-3", "3-2", "2-3", "3-3"])
        resultado_ponfe = st.selectbox(f"Resultado {pon_local} vs {pon_visitante}", ["", "1", "X", "2"])

        if st.button("✅ Evaluar porra"):
            df_filtrado = df.copy()

            if resultado_rm:
                gl_rm, gv_rm = map(int, resultado_rm.split("-"))
                esperado_rm = f"{gl_rm}-{gv_rm}" if rm_local == "Real Madrid" else f"{gv_rm}-{gl_rm}"
                df_filtrado = df_filtrado[df_filtrado["Real Madrid"].astype(str) == esperado_rm]

            if resultado_bar:
                gl_bar, gv_bar = map(int, resultado_bar.split("-"))
                esperado_bar = f"{gl_bar}-{gv_bar}" if bar_local == "Barcelona" else f"{gv_bar}-{gl_bar}"
                df_filtrado = df_filtrado[df_filtrado["Barcelona"].astype(str) == esperado_bar]

            if resultado_ponfe in ["1", "X", "2"]:
                if pon_local == "Ponferradina":
                    resultado_real_ponfe = resultado_ponfe
                else:
                    resultado_real_ponfe = "2" if resultado_ponfe == "1" else "1" if resultado_ponfe == "2" else "X"
                df_filtrado = df_filtrado[df_filtrado["Ponferradina"].astype(str) == resultado_real_ponfe]

            st.subheader("🎯 Participantes que siguen vivos:")
            if not df_filtrado.empty:
                st.dataframe(df_filtrado.astype(str))
            else:
                st.warning("😢 No ha acertado nadie. Todos eliminados.")

            data_resultados = {
                "partidos": {
                    "Real Madrid": f"{rm_local} vs {rm_visitante}",
                    "Barcelona": f"{bar_local} vs {bar_visitante}",
                    "Ponferradina": f"{pon_local} vs {pon_visitante}"
                },
                "resultados": {
                    "Real Madrid": resultado_rm,
                    "Barcelona": resultado_bar,
                    "Ponferradina": resultado_ponfe
                },
                "horarios": {
                    "Real Madrid": {"fecha": str(fecha_rm), "hora": str(hora_rm)},
                    "Barcelona": {"fecha": str(fecha_bar), "hora": str(hora_bar)},
                    "Ponferradina": {"fecha": str(fecha_ponfe), "hora": str(hora_ponfe)}
                }
            }
            os.makedirs("data", exist_ok=True)
            with open("data/resultados.json", "w") as f:
                json.dump(data_resultados, f)
            df_filtrado.astype(str).to_csv("data/supervivientes.csv", index=False)
            df.astype(str).to_excel("data/predicciones.xlsx", index=False)
            st.success("📁 Datos guardados correctamente para los participantes.")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
