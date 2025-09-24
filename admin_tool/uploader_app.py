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
CLEANER_SCRIPT_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_inscripciones.py')
IMPORTER_SCRIPT_PATH = os.path.join(DB_SCRIPTS_DIR, 'inscripciones_cursadas.py')

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

def mostrar_resumen_inscripciones():
    """Consulta la base de datos y muestra un resumen de las inscripciones por período."""
    st.subheader("Resumen de Inscripciones a Cursadas por Período")
    try:
        db_path = os.path.join(BASE_DIR, 'data', 'base_de_datos', 'academica.db')
        conn = sqlite3.connect(db_path)
        
        query = "SELECT periodo, COUNT(*) as total FROM inscripciones_cursadas GROUP BY periodo ORDER BY periodo DESC"
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if not df.empty:
            st.write("Total de inscripciones por período en la base de datos:")
            # Usar st.dataframe para una mejor visualización
            st.dataframe(df.rename(columns={'periodo': 'Período', 'total': 'Total Inscripciones'}).set_index('Período'))
        else:
            st.info("No hay datos de inscripciones en la base de datos para mostrar.")
            
    except Exception as e:
        st.error(f"Ocurrió un error al consultar la base de datos: {e}")

# --- Interfaz de Usuario ---
st.title("Herramienta de Carga de Datos Académicos")

# --- Paso 1: Tipo de Importación ---
st.header("Paso 1: Tipo de Importación")
tipo_importacion = st.selectbox(
    "Seleccionar tipo de importación:",
    ["Inscripciones a Cursadas"] #, "Inscripciones a Carreras", "Egresados"]
)

# --- Paso 2: Período Lectivo ---
st.header("Paso 2: Período Lectivo")
periodos_disponibles = generar_periodos()
periodo_seleccionado = st.selectbox(
    "Seleccionar período lectivo:",
    periodos_disponibles
)

# --- Paso 3: Cargar Archivo ---
st.header("Paso 3: Cargar Archivo")
archivo_subido = st.file_uploader(
    "Cargar el archivo Excel de inscripciones:",
    type=['xlsx']
)

# --- Paso 4: Ejecutar Proceso ---
st.header("Paso 4: Ejecutar Proceso")
if st.button("Procesar y Cargar Datos"):
    if not tipo_importacion:
        st.warning("Por favor, selecciona un tipo de importación.")
    elif not periodo_seleccionado:
        st.warning("Por favor, selecciona un período lectivo.")
    elif archivo_subido is None:
        st.warning("Por favor, carga un archivo Excel.")
    else:
        st.info("Iniciando el proceso de carga... No cierres esta ventana.")

        # --- Lógica del Backend ---
        
        # 1. Guardar archivo temporalmente
        temp_filename = f"inscripciones_temp_{periodo_seleccionado}.xlsx"
        temp_filepath = os.path.join(RAW_DATA_DIR, temp_filename)
        
        with open(temp_filepath, "wb") as f:
            f.write(archivo_subido.getbuffer())
        st.success(f"Archivo temporal guardado en: `{temp_filepath}`")

        # 2. Ejecutar script de limpieza
        st.subheader("Ejecutando script de limpieza...")
        processed_filename = f"inscripciones_procesado_{periodo_seleccionado}.csv"
        processed_filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)
        
        comando_limpieza = [
            "python", CLEANER_SCRIPT_PATH,
            "--periodo", periodo_seleccionado,
            "--archivo-entrada", temp_filepath,
            "--archivo-salida", processed_filepath
        ]
        
        limpieza_exitosa, out_limpieza = ejecutar_proceso(comando_limpieza)

        # 3. Ejecutar script de importación a DB
        if limpieza_exitosa:
            st.subheader("Ejecutando script de importación a la base de datos...")
            comando_importacion = [
                "python", IMPORTER_SCRIPT_PATH,
                "--archivo-csv", processed_filepath
            ]
            importacion_exitosa, out_importacion = ejecutar_proceso(comando_importacion)
            
            if importacion_exitosa:
                st.balloons()
                st.success("¡Proceso completado con éxito!")
                st.info(f"Resumen de la importación:\n{out_importacion}")
                mostrar_resumen_inscripciones()
        else:
            st.error("El proceso se detuvo debido a un error en el script de limpieza.")

        # 4. Limpieza de archivo temporal
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            st.info(f"Archivo temporal `{temp_filename}` eliminado.")
