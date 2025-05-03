import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import requests

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
import streamlit as st
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

# Alias de equipos para adaptarlos a nombres de la API
equipo_alias = {
    "Barcelona B": "Barcelona Atlètic",
    "Celta B": "Celta Vigo B",
    "Osasuna B": "Osasuna Promesas",
    "Real Unión": "Real Union",
    "Bilbao Athletic": "Athletic Club B",
    "Gimnástica Segoviana": "G. Segoviana",
    "Atlético": "Atlético de Madrid",
    "Athletic": "Athletic Club",
    "R. Sociedad": "Real Sociedad",
    "Rayo": "Rayo Vallecano",
    "Alavés": "Deportivo Alavés",
    "Leganés": "CD Leganés",
    "Real Valladolid": "Valladolid"
}

def formatear_equipo(nombre):
    return equipo_alias.get(nombre, nombre)

def obtener_resultado(nombre_local, nombre_visitante, fecha):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {
        "date": fecha,
        "season": datetime.now().year
    }
    headers = {
        "X-RapidAPI-Key": "TU_CLAVE_AQUI",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        st.error(f"❌ Error al consultar la API: {response.status_code}")
        return None
    data = response.json()
    for match in data.get("response", []):
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        if (home == nombre_local and away == nombre_visitante) or (home == nombre_visitante and away == nombre_local):
            if match["goals"]["home"] is not None and match["goals"]["away"] is not None:
                return {
                    "local": home,
                    "visitante": away,
                    "goles_local": match["goals"]["home"],
                    "goles_visitante": match["goals"]["away"]
                }
    return None

# 🛰️ Consulta directa desde la nube
st.markdown("---")
st.subheader("🛰️ Consulta automática de resultados (vía API)")
auto_btn = st.button("Consultar resultados automáticamente ahora")
if auto_btn:
    if os.path.exists("data/resultados.json"):
        with open("data/resultados.json", "r") as f:
            datos = json.load(f)
        partidos = datos["partidos"]
        horarios = datos["horarios"]
        actualizados = {}
        ahora = datetime.now()
        for clave, horario in horarios.items():
            fecha = horario["fecha"]
            hora_str = horario["hora"][:5]
            hora_fin = datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M")
            if not (hora_fin <= ahora <= hora_fin + timedelta(hours=1)):
                st.info(f"⏳ {clave}: fuera del rango de comprobación ({hora_fin} +/- 1h)")
                continue
            local, visitante = partidos[clave].split(" vs ")
            local = formatear_equipo(local.strip())
            visitante = formatear_equipo(visitante.strip())
            with st.spinner(f"Buscando resultado para {local} vs {visitante}..."):
                resultado = obtener_resultado(local, visitante, fecha)
            if resultado:
                if clave in ["Real Madrid", "Barcelona"]:
                    es_local = (local == clave)
                    nuevo_resultado = f"{resultado['goles_local']}-{resultado['goles_visitante']}" if es_local else f"{resultado['goles_visitante']}-{resultado['goles_local']}"
                else:
                    g_local = resultado['goles_local']
                    g_visit = resultado['goles_visitante']
                    if g_local > g_visit:
                        nuevo_resultado = "1"
                    elif g_local < g_visit:
                        nuevo_resultado = "2"
                    else:
                        nuevo_resultado = "X"
                datos["resultados"][clave] = nuevo_resultado
                actualizados[clave] = nuevo_resultado
                st.success(f"✅ {clave} = {nuevo_resultado}")
            else:
                st.warning(f"⚠️ Resultado aún no disponible para {clave}.")
        if actualizados:
            with open("data/resultados.json", "w") as f:
                json.dump(datos, f)
            if os.path.exists("data/predicciones.xlsx"):
                df = pd.read_excel("data/predicciones.xlsx")
                df_filtrado = df.copy()
                for clave, resultado in datos["resultados"].items():
                    df_filtrado = df_filtrado[df_filtrado[clave].astype(str) == resultado]
                df_filtrado.astype(str).to_csv("data/supervivientes.csv", index=False)
                st.success("🎯 Supervivientes actualizados correctamente.")
        elif not actualizados:
            st.info("ℹ️ No se ha actualizado ningún resultado.")
    else:
        st.error("❌ No se encontró el archivo resultados.json. Asegúrate de haber evaluado al menos una jornada.")

# 📝 Sección para configurar partidos y cargar predicciones
st.markdown("---")
st.subheader("📅 Selecciona los equipos y horarios de cada partido")

col1, col2 = st.columns(2)
with col1:
    partido_rm_local = st.selectbox("🏠 Local (RM)", equipos_laliga)
with col2:
    partido_rm_visitante = st.selectbox("🚗 Visitante (RM)", equipos_laliga)
fecha_rm = st.date_input("Fecha del partido (RM)")
hora_rm = st.time_input("Hora estimada de finalización (RM)")

col3, col4 = st.columns(2)
with col3:
    partido_bar_local = st.selectbox("🏠 Local (BAR)", equipos_laliga)
with col4:
    partido_bar_visitante = st.selectbox("🚗 Visitante (BAR)", equipos_laliga)
fecha_bar = st.date_input("Fecha del partido (BAR)")
hora_bar = st.time_input("Hora de finalización (BAR)")

col5, col6 = st.columns(2)
with col5:
    partido_ponf_local = st.selectbox("🏠 Local (Ponfe)", equipos_primera_federacion)
with col6:
    partido_ponf_visitante = st.selectbox("🚗 Visitante (Ponfe)", equipos_primera_federacion)
fecha_ponf = st.date_input("Fecha del partido (Ponfe)")
hora_ponf = st.time_input("Hora estimada de finalización (Ponfe)")

archivo_excel = st.file_uploader("📤 Sube el archivo Excel con las predicciones", type=["xlsx"])

if archivo_excel:
    try:
        df = pd.read_excel(archivo_excel)
        st.success("✅ Archivo cargado correctamente.")
        st.subheader("🔍 Vista previa de las predicciones:")
        st.dataframe(df, use_container_width=True)

        st.subheader("🎯 Introduce los resultados reales")
        resultado_rm = st.text_input(f"Resultado {partido_rm_local} vs {partido_rm_visitante} (ej: 2-1)")
        resultado_bar = st.text_input(f"Resultado {partido_bar_local} vs {partido_bar_visitante} (ej: 1-0)")
        resultado_ponf = st.selectbox(f"Resultado {partido_ponf_local} vs {partido_ponf_visitante}", ["", "1", "X", "2"])

        if st.button("Evaluar porra"):
            try:
                df.to_excel("data/predicciones.xlsx", index=False)

                resultados = {
                    "Real Madrid": resultado_rm,
                    "Barcelona": resultado_bar,
                    "Ponferradina": resultado_ponf
                }
                partidos = {
                    "Real Madrid": f"{partido_rm_local} vs {partido_rm_visitante}",
                    "Barcelona": f"{partido_bar_local} vs {partido_bar_visitante}",
                    "Ponferradina": f"{partido_ponf_local} vs {partido_ponf_visitante}"
                }
                horarios = {
                    "Real Madrid": {"fecha": str(fecha_rm), "hora": str(hora_rm)},
                    "Barcelona": {"fecha": str(fecha_bar), "hora": str(hora_bar)},
                    "Ponferradina": {"fecha": str(fecha_ponf), "hora": str(hora_ponf)}
                }

                with open("data/resultados.json", "w") as f:
                    json.dump({"resultados": resultados, "partidos": partidos, "horarios": horarios}, f)

                df_filtrado = df.copy()
                for clave, resultado in resultados.items():
                    df_filtrado = df_filtrado[df_filtrado[clave].astype(str) == resultado]

                df_filtrado.astype(str).to_csv("data/supervivientes.csv", index=False)

                st.success("🏆 Evaluación completada. ¡Suerte a todos!")
            except Exception as e:
                st.error(f"❌ Error al evaluar la porra: {e}")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
else:
    st.info("🔔 Para evaluar la porra, primero sube un archivo Excel.")
