
import pandas as pd
import sqlite3
import os

# --- Configuración ---
DB_PATH = 'data/base_de_datos/academica.db'
OUTPUT_DIR = '_output/inscripciones_carreras'

def generar_reportes_inscripciones():
    """
    Se conecta a la base de datos para generar los reportes CSV y KPIs
    necesarios para el dashboard de inscripciones a carreras.
    """
    print("Iniciando la generación de reportes de inscripciones a carreras...")

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
        df_inscriptos_dia = pd.read_sql_query("SELECT fecha_insc, COUNT(*) as cantidad FROM inscripciones_carreras GROUP BY fecha_insc ORDER BY fecha_insc;", conn)
        df_inscriptos_dia.to_csv(os.path.join(OUTPUT_DIR, 'inscriptos_por_dia.csv'), index=False)

        # Tarea 3.2: Generar inscriptos_vs_preinscriptos_por_carrera.csv
        print("-> Generando inscriptos_vs_preinscriptos_por_carrera.csv...")
        df_preinscriptos = pd.read_sql_query("SELECT carrera, COUNT(*) as preinscriptos FROM preinscriptos GROUP BY carrera;", conn)
        df_inscriptos = pd.read_sql_query("SELECT carrera, COUNT(*) as inscriptos FROM inscripciones_carreras WHERE estado_insc = 'Aceptada' GROUP BY carrera;", conn)
        df_comparativa = pd.merge(df_preinscriptos, df_inscriptos, on='carrera', how='outer').fillna(0)
        df_comparativa['inscriptos'] = df_comparativa['inscriptos'].astype(int)
        df_comparativa.to_csv(os.path.join(OUTPUT_DIR, 'inscriptos_vs_preinscriptos_por_carrera.csv'), index=False)

        # Tarea 3.3: Generar preinscripciones_por_estado.csv
        print("-> Generando preinscripciones_por_estado.csv...")
        df_estado = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM preinscriptos GROUP BY estado;", conn)
        df_estado.to_csv(os.path.join(OUTPUT_DIR, 'preinscripciones_por_estado.csv'), index=False)

        # Fase 4.1: Generar KPIs
        print("-> Generando kpis_inscripciones_carreras.csv...")
        total_preinscriptos = pd.read_sql_query("SELECT COUNT(*) as total FROM preinscriptos;", conn)['total'][0]
        total_inscriptos = pd.read_sql_query("SELECT COUNT(*) as total FROM inscripciones_carreras WHERE estado_insc = 'Aceptada';", conn)['total'][0]
        tasa_conversion = (total_inscriptos / total_preinscriptos) * 100 if total_preinscriptos > 0 else 0
        estado_principal = pd.read_sql_query("SELECT estado FROM preinscriptos GROUP BY estado ORDER BY COUNT(*) DESC LIMIT 1;", conn)['estado'][0]

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
    generar_reportes_inscripciones()
