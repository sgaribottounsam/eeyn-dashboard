import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- Configuración ---
# Para cambiar el año de los reportes, simplemente modifica el valor de la variable YEAR.
# Por ejemplo, para generar reportes para el año 2026, cambia YEAR = 2025 a YEAR = 2026.
YEAR = 2025

DB_PATH = 'data/base_de_datos/academica.db'
OUTPUT_DIR = '_output/inscripciones_carreras'

def generar_reportes_inscripciones(year):
    """
    Se conecta a la base de datos para generar los reportes CSV y KPIs
    necesarios para el dashboard de inscripciones a carreras para un año específico.
    """
    print(f"Iniciando la generación de reportes de inscripciones a carreras para el año {year}...")

    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"-> Directorio de salida asegurado: {OUTPUT_DIR}")

    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"-> Conexión exitosa con la base de datos: {DB_PATH}")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return

    try:
        # Tarea 3.1: Generar inscriptos_por_dia.csv
        print("-> Generando inscriptos_por_dia.csv...")
        query_inscriptos_dia = f"SELECT fecha_insc, COUNT(*) as cantidad FROM inscripciones_carreras WHERE anio = {year} GROUP BY fecha_insc ORDER BY fecha_insc;"
        df_inscriptos_dia = pd.read_sql_query(query_inscriptos_dia, conn)
        df_inscriptos_dia.to_csv(os.path.join(OUTPUT_DIR, 'inscriptos_por_dia.csv'), index=False)

        # Tarea 3.2: Generar inscriptos_vs_preinscriptos_por_carrera.csv
        print("-> Generando inscriptos_vs_preinscriptos_por_carrera.csv...")
        query_preinscriptos = f"SELECT carrera, COUNT(*) as preinscriptos FROM preinscriptos WHERE anio = {year} GROUP BY carrera;"
        df_preinscriptos = pd.read_sql_query(query_preinscriptos, conn)
        
        query_inscriptos = f"SELECT carrera, COUNT(*) as inscriptos FROM inscripciones_carreras WHERE estado_insc = 'Aceptada' AND anio = {year} GROUP BY carrera;"
        df_inscriptos = pd.read_sql_query(query_inscriptos, conn)
        
        df_comparativa = pd.merge(df_preinscriptos, df_inscriptos, on='carrera', how='outer').fillna(0)
        df_comparativa['inscriptos'] = df_comparativa['inscriptos'].astype(int)
        df_comparativa.to_csv(os.path.join(OUTPUT_DIR, 'inscriptos_vs_preinscriptos_por_carrera.csv'), index=False)

        # Tarea 3.3: Generar preinscripciones_por_estado.csv
        print("-> Generando preinscripciones_por_estado.csv...")
        query_estado = f"SELECT estado, COUNT(*) as cantidad FROM preinscriptos WHERE anio = {year} GROUP BY estado;"
        df_estado = pd.read_sql_query(query_estado, conn)
        df_estado.to_csv(os.path.join(OUTPUT_DIR, 'preinscripciones_por_estado.csv'), index=False)

        # Tarea 3.4: Generar inscriptos_grado_por_dia.csv
        print("-> Generando inscriptos_grado_por_dia.csv...")
        query_grado_diario = f"""
            SELECT
                i.fecha_insc
            FROM inscripciones_carreras AS i
            JOIN propuestas AS p ON i.carrera = p.codigo
            WHERE p.tipo = 'Grado' AND i.anio = {year}
        """
        df_grado_diario = pd.read_sql_query(query_grado_diario, conn)
        
        if not df_grado_diario.empty:
            df_grado_diario['fecha_insc'] = pd.to_datetime(df_grado_diario['fecha_insc'], errors='coerce')
            df_grado_diario.dropna(subset=['fecha_insc'], inplace=True)
            
            df_conteo_diario = df_grado_diario.groupby('fecha_insc').size().reset_index(name='cantidad')
            df_conteo_diario.to_csv(os.path.join(OUTPUT_DIR, 'inscriptos_grado_por_dia.csv'), index=False)
            print(f"-> Se generó 'inscriptos_grado_por_dia.csv' con {len(df_conteo_diario)} registros de fechas.")
        else:
            print("-> No se encontraron inscripciones de grado para generar 'inscriptos_grado_por_dia.csv'.")

        # Fase 4.1: Generar KPIs
        print("-> Generando kpis_inscripciones_carreras.csv...")
        query_total_preinscriptos = f"SELECT COUNT(*) as total FROM preinscriptos WHERE anio = {year};"
        total_preinscriptos = pd.read_sql_query(query_total_preinscriptos, conn)['total'][0]

        query_total_inscriptos = f"SELECT COUNT(*) as total FROM inscripciones_carreras WHERE estado_insc = 'Aceptada' AND anio = {year};"
        total_inscriptos = pd.read_sql_query(query_total_inscriptos, conn)['total'][0]
        
        tasa_conversion = (total_inscriptos / total_preinscriptos) * 100 if total_preinscriptos > 0 else 0
        
        query_estado_principal = f"SELECT estado FROM preinscriptos WHERE anio = {year} GROUP BY estado ORDER BY COUNT(*) DESC LIMIT 1;"
        estado_principal_series = pd.read_sql_query(query_estado_principal, conn)
        estado_principal = estado_principal_series['estado'][0] if not estado_principal_series.empty else 'N/A'


        kpis = {
            'Total Preinscriptos': [total_preinscriptos],
            'Total Inscriptos Aceptados': [total_inscriptos],
            'Tasa de Conversión (%)': [round(tasa_conversion, 2)],
            'Principal Estado Preinscripción': [estado_principal]
        }
        df_kpis = pd.DataFrame(kpis)
        df_kpis.to_csv(os.path.join(OUTPUT_DIR, 'kpis_inscripciones_carreras.csv'), index=False)

        print("\nReportes generados exitosamente.")

    except Exception as e:
        print(f"Ocurrió un error durante la generación de reportes: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

if __name__ == '__main__':
    generar_reportes_inscripciones(YEAR)