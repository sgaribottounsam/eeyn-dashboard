import pandas as pd
import os
import sqlite3

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
    "egresados": "egresados",
    "insc_carreras": "inscripciones_carreras"
}


# --- Carga de Datos ---

def cargar_evolucion_egresados():
    """Carga el archivo CSV con el detalle de egresados por año, carrera y plan."""
    try:
        folder = SUB_PATHS["egresados"]
        file_path = os.path.join(DATA_PATH, folder, 'Egresados_anio_egreso_carrera.csv')
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"-> Archivo Egresados_anio_egreso_carrera.csv cargado correctamente.")
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
                # Proceso robusto por columna para evitar problemas de tipos
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
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
                # Proceso robusto por columna para evitar problemas de tipos
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
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

# --- Funciones para la página de Inscripciones a Carreras ---

def cargar_kpis_inscripciones_carreras():
    """Carga los KPIs desde el archivo CSV de inscripciones a carreras."""
    try:
        folder = SUB_PATHS["insc_carreras"]
        file_path = os.path.join(DATA_PATH, folder, 'kpis_inscripciones_carreras.csv')
        df_kpi = pd.read_csv(file_path, encoding='utf-8')
        return df_kpi.to_dict(orient='records')[0]
    except (FileNotFoundError, IndexError):
        print(f"Advertencia: No se encontró o está vacío el archivo en {file_path}")
        return {}

def cargar_inscriptos_por_dia():
    """Carga la evolución de inscriptos por día."""
    try:
        folder = SUB_PATHS["insc_carreras"]
        file_path = os.path.join(DATA_PATH, folder, 'inscriptos_por_dia.csv')
        df = pd.read_csv(file_path, encoding='utf-8', parse_dates=['fecha_insc'])
        return df
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_comparativa_inscriptos_carrera():
    """Carga la comparación de inscriptos vs preinscriptos por carrera."""
    try:
        folder = SUB_PATHS["insc_carreras"]
        file_path = os.path.join(DATA_PATH, folder, 'inscriptos_vs_preinscriptos_por_carrera.csv')
        return pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_preinscriptos_por_estado():
    """Carga la distribución de preinscriptos por estado."""
    try:
        folder = SUB_PATHS["insc_carreras"]
        file_path = os.path.join(DATA_PATH, folder, 'preinscripciones_por_estado.csv')
        return pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo en {file_path}")
        return pd.DataFrame()

def cargar_inscriptos_grado_por_dia():
    """
    Carga la evolución de inscriptos de grado por día directamente desde la BD,
    filtrando para los años y fechas de interés.
    """
    db_path = os.path.join(project_root, 'data', 'base_de_datos', 'academica.db')
    
    query = """
        SELECT
            ic.anio, -- Usar el año académico correcto
            strftime('%m-%d', ic.fecha_insc) AS dia_mes,
            COUNT(DISTINCT ic.n_documento) AS cantidad
        FROM inscripciones_carreras AS ic
        JOIN propuestas AS p ON ic.carrera = p.codigo
        WHERE ic.anio >= 2024 -- Filtrar por año académico
          AND (
            (strftime('%m', ic.fecha_insc) = '10') OR
            (strftime('%m', ic.fecha_insc) = '11' AND strftime('%d', ic.fecha_insc) <= '15')
          )
          AND p.tipo = 'Grado'
        GROUP BY ic.anio, dia_mes
        ORDER BY ic.anio, dia_mes;
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        print("-> Datos de inscriptos diarios por grado cargados desde la BD.")
        return df
    except Exception as e:
        print(f"Error al consultar la base de datos para inscriptos diarios: {e}")
        return pd.DataFrame()

def cargar_inscripciones_por_anio_carrera():
    """
    Carga el conteo de inscripciones por año y carrera (solo Grado) desde la BD.
    """
    db_path = os.path.join(project_root, 'data', 'base_de_datos', 'academica.db')
    query = """
        SELECT
            ic.anio,
            ic.carrera AS carrera_codigo,
            p.nombre AS carrera_nombre,
            COUNT(ic.n_documento) AS cantidad
        FROM inscripciones_carreras AS ic
        JOIN propuestas AS p ON ic.carrera = p.codigo
        WHERE p.tipo = 'Grado'
        GROUP BY ic.anio, carrera_codigo, carrera_nombre
        ORDER BY ic.anio, carrera_nombre;
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        print("-> Datos de inscripciones por año y carrera cargados desde la BD.")
        return df
    except Exception as e:
        print(f"Error al consultar la base de datos para inscripciones por año/carrera: {e}")
        return pd.DataFrame()

def cargar_documentacion_por_dia():
    """
    Carga la evolución de la recepción de documentación por día y estado.
    """
    db_path = os.path.join(project_root, 'data', 'base_de_datos', 'academica.db')
    
    query = """
        SELECT
            DATE(marca_temporal) as fecha,
            CASE
                WHEN estado_documentacin IS NULL OR estado_documentacin = '' OR estado_documentacin = 'Para revisar' THEN 'Revisar'
                ELSE estado_documentacin
            END as estado_agrupado,
            COUNT(*) as cantidad
        FROM docu_inscripciones
        WHERE marca_temporal >= '2025-10-01'
        GROUP BY fecha, estado_agrupado
        ORDER BY fecha, estado_agrupado;
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Pivotear la tabla para tener los estados como columnas
        df_pivot = df.pivot_table(index='fecha', columns='estado_agrupado', values='cantidad', fill_value=0).reset_index()
        
        # Asegurarse de que todas las columnas de estado esperadas existan
        estados_esperados = ['Aprobada', 'Rechazada', 'Duplicado', 'Revisar']
        for estado in estados_esperados:
            if estado not in df_pivot.columns:
                df_pivot[estado] = 0
        
        print("-> Datos de documentación por día cargados desde la BD.")
        return df_pivot
    except Exception as e:
        print(f"Error al consultar la base de datos para documentación por día: {e}")
        return pd.DataFrame()

def cargar_inscriptos_grado_y_pregrado_por_dia():
    """
    Carga la evolución de inscriptos de grado y pregrado por día directamente desde la BD,
    filtrando para los años y fechas de interés.
    """
    db_path = os.path.join(project_root, 'data', 'base_de_datos', 'academica.db')
    
    query = """
        SELECT
            ic.anio, -- Usar el año académico correcto
            strftime('%m-%d', ic.fecha_insc) AS dia_mes,
            COUNT(DISTINCT ic.n_documento) AS cantidad
        FROM inscripciones_carreras AS ic
        JOIN propuestas AS p ON ic.carrera = p.codigo
        WHERE ic.anio >= 2024 -- Filtrar por año académico
          AND p.tipo IN ('Grado', 'Pregrado')
          AND (
            (strftime('%m', ic.fecha_insc) = '10') OR
            (strftime('%m', ic.fecha_insc) = '11' AND strftime('%d', ic.fecha_insc) <= '15')
          )
        GROUP BY ic.anio, dia_mes
        ORDER BY ic.anio, dia_mes;
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        print("-> Datos de inscriptos diarios de grado y pregrado cargados desde la BD.")
        return df
    except Exception as e:
        print(f"Error al consultar la base de datos para inscriptos diarios de grado y pregrado: {e}")
        return pd.DataFrame()
