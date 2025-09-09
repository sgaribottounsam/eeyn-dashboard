import pandas as pd
import os

# --- Path a la Carpeta de Datos (Método Robusto) ---
# 1. Obtenemos la ruta absoluta del directorio donde está ESTE archivo (loader.py).
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Subimos un nivel para llegar a la carpeta de la app (dash_dashboard).
app_dir = os.path.dirname(current_file_dir)
# 3. Subimos otro nivel para llegar a la raíz del proyecto grande.
project_root = os.path.dirname(app_dir)
# 4. Construimos la ruta a la carpeta _output desde la raíz del proyecto.
DATA_PATH = os.path.join(project_root, "_output")


# --- Configuración de Sub-carpetas de Datos ---
SUB_PATHS = {
    "insc_materias": "inscripciones_materias",
    "egresados": "egresados"
}


# --- Carga de Datos ---

def cargar_egresados_por_anio():
    """Carga el archivo CSV con el resumen de egresados por año y carrera."""
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_anio_egreso.csv')
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"-> Archivo Egresados_anio_egreso.csv cargado correctamente.")
        return df
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_kpis_inscripciones():
    """Carga los KPIs desde el archivo CSV de inscripciones."""
    try:
        folder = SUB_PATHS["insc_materias"]
        file_path = os.path.join(DATA_PATH, folder, 'KPI_insc_materias.csv')
        df_kpi = pd.read_csv(file_path, header=None, names=['Indicador', 'Valor'], decimal=',')
        return {row['Indicador']: row['Valor'] for _, row in df_kpi.iterrows()}
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return {}

def cargar_kpis_egresados():
    """Carga los KPIs desde el archivo CSV de egresados."""
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_KPI.csv')
        df_kpi = pd.read_csv(file_path, encoding='utf-8', header=None, names=['Indicador', 'Valor'], decimal=',')
        return {row['Indicador']: row['Valor'] for _, row in df_kpi.iterrows()}
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return {}

def cargar_evolucion_todas():
    try:
        folder = SUB_PATHS["insc_materias"]
        file_path = os.path.join(DATA_PATH, folder, 'TODAS_evolucion.csv')
        df = pd.read_csv(file_path, encoding='utf-8')
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)
        df = df.dropna(how='all')
        return df[~df['Inscripciones'].str.contains('Total', na=False)]
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_evolucion_grado():
    try:
        folder = SUB_PATHS["insc_materias"]
        file_path = os.path.join(DATA_PATH, folder, 'GRADO_evolucion.csv')
        df = pd.read_csv(file_path, encoding='utf-8')
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)
        df = df.dropna(how='all')
        return df[~df['Inscripciones'].str.contains('Total', na=False)]
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_cpu_materias():
    try:
        folder = SUB_PATHS["insc_materias"]
        file_path = os.path.join(DATA_PATH, folder, 'CPU_cantidad_materias.csv')
        return pd.read_csv(file_path, decimal=',', encoding='utf-8')
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_datos_egresados():
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_duración.csv')
        df = pd.read_csv(file_path, encoding='utf-8', decimal=',')
        df.columns = ['Carrera - Plan', 'Cantidad desde 1994', 'Duración promedio', 'Cantidad (Inscriptos 2009 en adelante)', 'Duración (2009 en adelante)']
        return df
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_egresados_2024():
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_2024.csv')
        df = pd.read_csv(file_path, encoding='utf-8', decimal=',')
        df.columns = ['Carrera', 'Cantidad', 'Duración Promedio']
        return df[df['Carrera'] != 'Total']
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_egresados_tasa():
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_tasa.csv')
        df = pd.read_csv(file_path, encoding='utf-8', decimal=',')
        df['Tasa'] = df['Tasa'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        return df
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

