import streamlit as st
import pandas as pd
import subprocess
import os
import datetime
import sqlite3

# --- Configuración de la App ---
st.set_page_config(page_title="Cargador de Datos Académicos", layout="centered")

# --- Rutas (relativas a la raíz del proyecto 'Dashboard') ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'crudos')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'procesados')
DB_SCRIPTS_DIR = os.path.join(BASE_DIR, 'db_scripts')
DB_PATH = os.path.join(BASE_DIR, 'data', 'base_de_datos', 'academica.db')

# --- Rutas a Scripts ---
# Cursadas
CLEANER_CURSADAS_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_inscripciones.py')
IMPORTER_CURSADAS_PATH = os.path.join(DB_SCRIPTS_DIR, 'inscripciones_cursadas.py')
# Carreras
CLEANER_CARRERAS_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_inscripciones_carreras.py')
IMPORTER_CARRERAS_PATH = os.path.join(DB_SCRIPTS_DIR, 'importador_inscripciones_carreras.py')
# Preinscripciones
CLEANER_PREINSCR_PATH = os.path.join(BASE_DIR, 'limpiadores', 'limpiador_preinscriptos.py')
IMPORTER_PREINSCR_PATH = os.path.join(DB_SCRIPTS_DIR, 'importador_preinscriptos.py')


# --- Funciones de Utilidad ---
def ejecutar_proceso(comando):
    """Ejecuta un comando de subproceso y muestra la salida en Streamlit."""
    st.write(f"Ejecutando: `{ ' '.join(comando)}`")
    # Usar la python del venv para asegurar consistencia
    comando[0] = os.path.join(BASE_DIR, '.venv', 'bin', 'python')
    
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

def ejecutar_comando_shell(comando, cwd, check=True):
    """Ejecuta un comando de shell y muestra la salida en Streamlit.

    Args:
        comando (str): El comando a ejecutar.
        cwd (str): El directorio de trabajo.
        check (bool): Si es True, lanza una excepción en caso de error.

    Returns:
        subprocess.CompletedProcess or subprocess.CalledProcessError: 
        El objeto de proceso completado o la excepción capturada.
    """
    st.write(f"Ejecutando: `{comando}`")
    try:
        process = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=check,
            encoding='utf-8'
        )
        # Solo mostrar salida stdout en caso de éxito si el check está activado
        if process.stdout and check:
            st.info(f"Salida:\n{process.stdout}")
        if check:
            st.success("Comando ejecutado con éxito.")
        return process
    except subprocess.CalledProcessError as e:
        # Si check=True, la excepción es capturada y devuelta
        error_details = f"Error al ejecutar el comando (código: {e.returncode})"
        if e.stdout:
            error_details += f"\n--- Salida (stdout) ---\n{e.stdout}"
        if e.stderr:
            error_details += f"\n--- Error (stderr) ---\n{e.stderr}"
        st.error(error_details)
        return e

# --- Funciones de Resumen ---
def mostrar_resumen(nombre_tabla, columna_grupo, titulo, nombre_col_grupo, nombre_col_total):
    st.subheader(titulo)
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT {columna_grupo}, COUNT(*) as total FROM {nombre_tabla} GROUP BY {columna_grupo} ORDER BY {columna_grupo} DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            st.write(f"Total de registros por {columna_grupo} en la base de datos:")
            st.dataframe(df.rename(columns={columna_grupo: nombre_col_grupo, 'total': nombre_col_total}).set_index(nombre_col_grupo))
        else:
            st.info(f"No hay datos de {nombre_tabla} en la base de datos.")
            
    except Exception as e:
        st.error(f"Ocurrió un error al consultar la base de datos: {e}")

# --- Interfaz de Usuario ---
st.title("Herramienta de Carga de Datos Académicos")

# --- Paso 1: Tipo de Importación ---
st.header("Paso 1: Seleccionar Tipo de Importación")
tipo_importacion = st.selectbox(
    "Seleccionar el tipo de datos que deseas importar:",
    ["Inscripciones a Carreras", "Preinscripciones", "Inscripciones a Cursadas"]
)

# --- Paso 2: Período o Año ---
st.header("Paso 2: Seleccionar Período o Año")
if tipo_importacion == "Inscripciones a Cursadas":
    # Lógica para Cursadas (no se usa en este caso)
    st.info("Lógica de selección de período para cursadas no implementada en este ejemplo.")
    info_paso_2 = "N/A"
else:
    current_year = datetime.date.today().year
    anios_disponibles = list(range(2020, current_year + 2))
    anio_seleccionado = st.selectbox(
        f"Seleccionar año de '{tipo_importacion}':",
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
        
        # Determinar qué scripts y nombres de archivo usar
        if tipo_importacion == "Inscripciones a Carreras":
            CLEANER_PATH = CLEANER_CARRERAS_PATH
            IMPORTER_PATH = IMPORTER_CARRERAS_PATH
            temp_filename_base = "inscripciones_carreras_temp"
            processed_filename_base = "inscripciones_carreras_procesado"
            resumen_func = lambda: mostrar_resumen('inscripciones_carreras', 'anio', 'Resumen de Inscripciones a Carreras', 'Año', 'Total Inscripciones')
        
        elif tipo_importacion == "Preinscripciones":
            CLEANER_PATH = CLEANER_PREINSCR_PATH
            IMPORTER_PATH = IMPORTER_PREINSCR_PATH
            temp_filename_base = "preinscripciones_temp"
            processed_filename_base = "preinscriptos_procesado"
            resumen_func = lambda: mostrar_resumen('preinscriptos', 'estado', 'Resumen de Preinscripciones por Estado', 'Estado', 'Total')

        # Lógica de ejecución común
        temp_filename = f"{temp_filename_base}_{info_paso_2}.xlsx"
        temp_filepath = os.path.join(RAW_DATA_DIR, temp_filename)

        with open(temp_filepath, "wb") as f:
            f.write(archivo_subido.getbuffer())
        st.success(f"Archivo temporal guardado en: `{temp_filepath}`")

        st.subheader("Ejecutando script de limpieza...")
        processed_filename = f"{processed_filename_base}_{info_paso_2}.csv"
        processed_filepath = os.path.join(PROCESSED_DATA_DIR, processed_filename)

        comando_limpieza = [
            "python", CLEANER_PATH,
            "--archivo-entrada", temp_filepath,
            "--archivo-salida", processed_filepath,
            "--anio", str(info_paso_2)
        ]
        limpieza_exitosa, _ = ejecutar_proceso(comando_limpieza)

        if limpieza_exitosa:
            st.subheader("Ejecutando script de importación a la base de datos...")
            comando_importacion = ["python", IMPORTER_PATH, "--archivo-csv", processed_filepath]
            importacion_exitosa, _ = ejecutar_proceso(comando_importacion)

            if importacion_exitosa:
                st.balloons()
                st.success(f"¡Proceso de importación completado con éxito!")
                # Mostrar el resumen correspondiente
                resumen_func()
        else:
            st.error("El proceso se detuvo debido a un error en el script de limpieza.")

        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            st.info(f"Archivo temporal `{temp_filename}` eliminado.")

# --- Paso 5: Finalizar Actualización ---
st.header("Paso 5: Finalizar Actualización")
st.warning("Asegúrate de que todos los datos se hayan cargado correctamente antes de finalizar.")

if st.button("Finalizar actualización"):
    st.info("Iniciando el proceso para guardar los cambios en el repositorio...")

    # Determinar la ruta relativa de la DB para el comando git
    db_relative_path = os.path.relpath(DB_PATH, BASE_DIR)

    # --- 1. Git Add ---
    st.subheader("Paso 5.1: Agregando la base de datos al área de preparación (git add)")
    add_process = ejecutar_comando_shell(f"git add {db_relative_path}", cwd=BASE_DIR)

    if isinstance(add_process, subprocess.CompletedProcess):
        
        # --- 2. Configurar usuario de Git ---
        st.subheader("Paso 5.2: Configurando usuario de Git")
        user_name = "sgaribottounsam"
        user_email = "sgaribotto@unsam.edu.ar"
        
        config_user_proc = ejecutar_comando_shell(f'git config user.name "{user_name}"', cwd=BASE_DIR)
        config_email_proc = ejecutar_comando_shell(f'git config user.email "{user_email}"', cwd=BASE_DIR)

        if isinstance(config_user_proc, subprocess.CompletedProcess) and isinstance(config_email_proc, subprocess.CompletedProcess):
            
            # --- 3. Git Commit ---
            st.subheader("Paso 5.3: Creando el commit (git commit)")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Actualización de la base de datos {timestamp}"
            commit_message_shell = commit_message.replace('"', '\\"')
            
            # Ejecutamos commit sin 'check=True' para manejar el caso "no changes"
            commit_process = ejecutar_comando_shell(f'git commit -m "{commit_message_shell}"', cwd=BASE_DIR, check=False)
            
            commit_ok = False
            if commit_process.returncode == 0:
                st.success("Commit creado con éxito.")
                st.info(f"Salida:\n{commit_process.stdout}")
                commit_ok = True
            # Si el commit falla porque no hay cambios, también lo consideramos "ok" para hacer push
            elif "no changes added to commit" in commit_process.stdout or "sin cambios agregados al commit" in commit_process.stdout:
                st.warning("No se encontraron nuevos cambios para confirmar. Se intentará hacer push del commit anterior.")
                st.info(f"Salida de Git:\n{commit_process.stdout}")
                commit_ok = True
            else:
                # Otro tipo de error en el commit
                error_details = f"Error al ejecutar git commit (código: {commit_process.returncode})"
                if commit_process.stdout:
                    error_details += f"\n--- Salida (stdout) ---\n{commit_process.stdout}"
                if commit_process.stderr:
                    error_details += f"\n--- Error (stderr) ---\n{commit_process.stderr}"
                st.error(error_details)

            if commit_ok:
                # --- 4. Git Push ---
                st.subheader("Paso 5.4: Subiendo los cambios al repositorio (git push)")
                
                import toml
                secrets_file_path = os.path.join(BASE_DIR, '.streamlit', 'secrets.toml')
                pat = None
                try:
                    with open(secrets_file_path, 'r') as f:
                        secrets = toml.load(f)
                        pat = secrets.get("GIT_TOKEN")
                    if not pat:
                        st.error(f"Secreto 'GIT_TOKEN' no encontrado en '{secrets_file_path}'. Por favor, asegúrate de que el archivo existe y contiene `GIT_TOKEN = 'tu_nuevo_token'`.")
                        st.stop()
                except FileNotFoundError:
                    st.error(f"Archivo de secretos no encontrado en '{secrets_file_path}'. Por favor, crea el archivo y añade `GIT_TOKEN = 'tu_nuevo_token'`.")
                    st.stop()
                except Exception as e:
                    st.error(f"Error al leer el archivo de secretos '{secrets_file_path}': {e}")
                    st.stop()

                user = "sgaribottounsam"
                remote_url = "https://github.com/sgaribottounsam/eeyn-dashboard.git"
                push_url = f"https://{user}:{pat}@{remote_url.split('//')[1]}"
                
                push_process = ejecutar_comando_shell(f"git push {push_url}", cwd=BASE_DIR)
                if isinstance(push_process, subprocess.CompletedProcess):
                    st.snow()
                    st.success("¡Actualización completada y subida al repositorio!")
