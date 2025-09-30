import streamlit as st
import pandas as pd
import subprocess
import os
import datetime
import sqlite3

# --- Configuración de la App ---
st.set_page_config(page_title="Cargador de Datos Académicos", layout="centered")

# --- Rutas (relativas a la raíz del proyecto 'Dashboard') ---
# Se asume que la app se ejecuta desde la raíz del proyecto Dashboard
# Ejemplo: streamlit run admin_tool/uploader_app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'crudos')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'procesados')
DB_SCRIPTS_DIR = os.path.join(BASE_DIR, 'db_scripts')

# Scripts para Cursadas
CLEANER_CURSADAS_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_inscripciones.py')
IMPORTER_CURSADAS_PATH = os.path.join(DB_SCRIPTS_DIR, 'inscripciones_cursadas.py')

# Scripts para Carreras
CLEANER_CARRERAS_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_inscripciones_carreras.py')
IMPORTER_CARRERAS_PATH = os.path.join(DB_SCRIPTS_DIR, 'importador_inscripciones_carreras.py')


# --- Funciones de Utilidad ---
def generar_periodos():
    """Genera una lista de períodos desde 2010 hasta el año actual + 1."""
    current_year = datetime.date.today().year
    periodos = []
    for year in range(2010, current_year + 2):
        periodos.append(f"{year}-1")
        periodos.append(f"{year}-2")
        # Los períodos de verano se agregaron después, puedes ajustar el inicio si es necesario
        if year >= 2015:
            periodos.append(f"{year}-3")
    return sorted(periodos, reverse=True)

def ejecutar_proceso(comando):
    """Ejecuta un comando de subproceso y muestra la salida en Streamlit."""
    st.write(f"Ejecutando: `{ ' '.join(comando)}`")
    process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    
    stdout_placeholder = st.empty()
    stderr_placeholder = st.empty()
    
    stdout_output = ""
    stderr_output = ""

    for line in iter(process.stdout.readline, ''):
        stdout_output += line
        stdout_placeholder.info(f"Salida del script:\n{stdout_output}")

    for line in iter(process.stderr.readline, ''):
        stderr_output += line
        stderr_placeholder.error(f"Errores del script:\n{stderr_output}")
        
    process.wait()
    
    if process.returncode == 0:
        st.success("El script se ejecutó correctamente.")
        return True, stdout_output
    else:
        st.error(f"El script finalizó con un error (código: {process.returncode}).")
        return False, stderr_output

def mostrar_resumen_inscripciones_cursadas():
    """Consulta la base de datos y muestra un resumen de las inscripciones a cursadas por período."""
    st.subheader("Resumen de Inscripciones a Cursadas por Período")
    try:
        db_path = os.path.join(BASE_DIR, 'data', 'base_de_datos', 'academica.db')
        conn = sqlite3.connect(db_path)
        
        query = "SELECT periodo, COUNT(*) as total FROM inscripciones_cursadas GROUP BY periodo ORDER BY periodo DESC"
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if not df.empty:
            st.write("Total de inscripciones por período en la base de datos:")
            st.dataframe(df.rename(columns={'periodo': 'Período', 'total': 'Total Inscripciones'}).set_index('Período'))
        else:
            st.info("No hay datos de inscripciones a cursadas en la base de datos.")
            
    except Exception as e:
        st.error(f"Ocurrió un error al consultar la base de datos: {e}")

def mostrar_resumen_inscripciones_carreras():
    """Consulta la db y muestra un resumen de las inscripciones a carreras por año."""
    st.subheader("Resumen de Inscripciones a Carreras por Año")
    try:
        db_path = os.path.join(BASE_DIR, 'data', 'base_de_datos', 'academica.db')
        conn = sqlite3.connect(db_path)
        
        query = "SELECT anio, COUNT(*) as total FROM inscripciones_carreras GROUP BY anio ORDER BY anio DESC"
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if not df.empty:
            st.write("Total de inscripciones por año en la base de datos:")
            st.dataframe(df.rename(columns={'anio': 'Año', 'total': 'Total Inscripciones'}).set_index('Año'))
        else:
            st.info("No hay datos de inscripciones a carreras en la base de datos.")
            
    except Exception as e:
        st.error(f"Ocurrió un error al consultar la base de datos: {e}")

# --- Interfaz de Usuario ---
st.title("Herramienta de Carga de Datos Académicos")

# --- Paso 1: Tipo de Importación ---
st.header("Paso 1: Seleccionar Tipo de Importación")
tipo_importacion = st.selectbox(
    "Seleccionar el tipo de datos que deseas importar:",
    ["Inscripciones a Cursadas", "Inscripciones a Carreras"] #, "Egresados"]
)

# --- Paso 2: Período o Año ---
st.header("Paso 2: Seleccionar Período o Año")
if tipo_importacion == "Inscripciones a Cursadas":
    periodos_disponibles = generar_periodos()
    periodo_seleccionado = st.selectbox(
        "Seleccionar período lectivo:",
        periodos_disponibles
    )
    info_paso_2 = periodo_seleccionado
elif tipo_importacion == "Inscripciones a Carreras":
    current_year = datetime.date.today().year
    anios_disponibles = list(range(2015, current_year + 2))
    anio_seleccionado = st.selectbox(
        "Seleccionar año de inscripción:",
        options=anios_disponibles,
        index=len(anios_disponibles)-1
    )
    info_paso_2 = anio_seleccionado

# --- Paso 3: Cargar Archivo ---
st.header("Paso 3: Cargar Archivo")
archivo_subido = st.file_uploader(
    f"Cargar el archivo Excel para '{tipo_importacion}':",
    type=['xlsx']
)

# --- Paso 4: Ejecutar Proceso ---
st.header("Paso 4: Ejecutar Proceso")
if st.button("Procesar y Cargar Datos"):
    if not all([tipo_importacion, info_paso_2, archivo_subido]):
        st.warning("Por favor, completa todos los pasos anteriores.")
    else:
        st.info("Iniciando el proceso de carga... No cierres esta ventana.")

        # --- Lógica para Inscripciones a Cursadas ---
        if tipo_importacion == "Inscripciones a Cursadas":
            temp_filename = f"inscripciones_temp_{info_paso_2}.xlsx"
            temp_filepath = os.path.join(RAW_DATA_DIR, temp_filename)
            
            with open(temp_filepath, "wb") as f:
                f.write(archivo_subido.getbuffer())
            st.success(f"Archivo temporal guardado en: `{temp_filepath}`")

            st.subheader("Ejecutando script de limpieza...")
            processed_filename = f"inscripciones_procesado_{info_paso_2}.csv"
            processed_filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
            
            comando_limpieza = [
                "python", CLEANER_CURSADAS_PATH,
                "--periodo", info_paso_2,
                "--archivo-entrada", temp_filepath,
                "--archivo-salida", processed_filepath
            ]
            limpieza_exitosa, _ = ejecutar_proceso(comando_limpieza)

            if limpieza_exitosa:
                st.subheader("Ejecutando script de importación a la base de datos...")
                comando_importacion = ["python", IMPORTER_CURSADAS_PATH, "--archivo-csv", processed_filepath]
                importacion_exitosa, out_importacion = ejecutar_proceso(comando_importacion)
                
                if importacion_exitosa:
                    st.balloons()
                    st.success("¡Proceso completado con éxito!")
                    mostrar_resumen_inscripciones_cursadas()
            else:
                st.error("El proceso se detuvo debido a un error en el script de limpieza.")

            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                st.info(f"Archivo temporal `{temp_filename}` eliminado.")

        # --- Lógica para Inscripciones a Carreras ---
        elif tipo_importacion == "Inscripciones a Carreras":
            temp_filename = f"inscripciones_carreras_temp_{info_paso_2}.xlsx"
            temp_filepath = os.path.join(RAW_DATA_DIR, temp_filename)

            with open(temp_filepath, "wb") as f:
                f.write(archivo_subido.getbuffer())
            st.success(f"Archivo temporal guardado en: `{temp_filepath}`")

            st.subheader("Ejecutando script de limpieza para carreras...")
            processed_filename = f"inscripciones_carreras_procesado_{info_paso_2}.csv"
            processed_filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)

            comando_limpieza = [
                "python", CLEANER_CARRERAS_PATH,
                "--archivo-entrada", temp_filepath,
                "--archivo-salida", processed_filepath,
                "--anio", str(info_paso_2)
            ]
            limpieza_exitosa, _ = ejecutar_proceso(comando_limpieza)

            if limpieza_exitosa:
                st.subheader("Ejecutando script de importación a la base de datos...")
                comando_importacion = ["python", IMPORTER_CARRERAS_PATH, "--archivo-csv", processed_filepath]
                importacion_exitosa, _ = ejecutar_proceso(comando_importacion)

                if importacion_exitosa:
                    st.balloons()
                    st.success("¡Proceso de importación de carreras completado con éxito!")
                    mostrar_resumen_inscripciones_carreras()
            else:
                st.error("El proceso se detuvo debido a un error en el script de limpieza.")

            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                st.info(f"Archivo temporal `{temp_filename}` eliminado.")
