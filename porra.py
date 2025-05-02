import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import requests

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

# Botón para ejecutar consulta directa desde la web
auto_btn = st.button("🛰️ Consultar resultados automáticamente ahora")
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
