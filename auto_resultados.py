import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import os

# Cargar datos guardados por porra.py
with open("data/resultados.json", "r") as f:
    datos = json.load(f)

partidos = datos["partidos"]
horarios = datos["horarios"]

headers = {
    "X-RapidAPI-Key": "TU_CLAVE_AQUI",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

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
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("Error al consultar API:", response.status_code)
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

# Comprobar si al menos un partido está en su ventana de comprobación
ahora = datetime.now()
partidos_en_rango = []
for clave, horario in horarios.items():
    fecha = horario["fecha"]
    hora_str = horario["hora"][:5]
    hora_fin = datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M")
    if hora_fin <= ahora <= hora_fin + timedelta(hours=1):
        partidos_en_rango.append(clave)

if not partidos_en_rango:
    print("No hay partidos en ventana de comprobación. Fin del script.")
    exit()

# Si hay partidos en rango, continuar con intentos
MAX_INTENTOS = 4
INTENTO_CADA_SEGUNDOS = 15 * 60

for intento in range(MAX_INTENTOS):
    print(f"\nIntento {intento + 1} de {MAX_INTENTOS}")
    actualizados = {}
    ahora = datetime.now()

    for clave in partidos_en_rango:
        horario = horarios[clave]
        fecha = horario["fecha"]
        hora_str = horario["hora"][:5]
        hora_fin = datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M")

        if ahora < hora_fin or ahora > hora_fin + timedelta(hours=1):
            print(f"{clave}: fuera del rango de comprobación ({hora_fin} +/- 1h)")
            continue

        local, visitante = partidos[clave].split(" vs ")
        local = formatear_equipo(local.strip())
        visitante = formatear_equipo(visitante.strip())

        print(f"Buscando resultado para {local} vs {visitante}...")
        resultado = obtener_resultado(local, visitante, fecha)

        if resultado:
            print(f"Resultado encontrado: {resultado['local']} {resultado['goles_local']} - {resultado['goles_visitante']} {resultado['visitante']}")
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
            print(f"Guardado: {clave} = {nuevo_resultado}")
        else:
            print(f"No disponible aún: {clave}")

    if actualizados:
        with open("data/resultados.json", "w") as f:
            json.dump(datos, f)

        if os.path.exists("data/predicciones.xlsx"):
            df = pd.read_excel("data/predicciones.xlsx")
            df_filtrado = df.copy()
            for clave, resultado in datos["resultados"].items():
                df_filtrado = df_filtrado[df_filtrado[clave].astype(str) == resultado]

            df_filtrado.astype(str).to_csv("data/supervivientes.csv", index=False)
            print("Supervivientes actualizados.")
        break
    else:
        if intento < MAX_INTENTOS - 1:
            print("Esperando 15 minutos para volver a comprobar...")
            time.sleep(INTENTO_CADA_SEGUNDOS)
        else:
            print("Finalizados los intentos. No se encontraron resultados.")
