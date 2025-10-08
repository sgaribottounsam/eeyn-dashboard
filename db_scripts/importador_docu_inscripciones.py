import pandas as pd
import sqlite3
import os

# --- Configuración ---
CSV_FILEPATH = 'data/procesados/inscripciones_docu_limpio.csv'
DB_FILEPATH = 'data/base_de_datos/academica.db'
TABLE_NAME = 'docu_inscripciones'

def importar_documentacion_inscripciones():
    """
    Importa los datos de documentación de inscripciones desde un CSV a una tabla SQLite.
    La tabla se borra y se vuelve a crear en cada ejecución para evitar duplicados.
    """
    print(f"Iniciando importación de '{CSV_FILEPATH}' a la tabla '{TABLE_NAME}'...")

    # --- Paso 1: Leer el archivo CSV procesado ---
    if not os.path.exists(CSV_FILEPATH):
        print(f"Error: No se encontró el archivo CSV en {CSV_FILEPATH}")
        return

    try:
        df = pd.read_csv(CSV_FILEPATH, encoding='utf-8')
        df['dni'] = df['dni'].astype(str)

        # Convertir 'marca_temporal' a formato de fecha (YYYY-MM-DD)
        if 'marca_temporal' in df.columns:
            print("-> Convirtiendo la columna 'marca_temporal' a formato de fecha (YYYY-MM-DD)...")
            df['marca_temporal'] = pd.to_datetime(df['marca_temporal'], format='%d/%m/%Y %H:%M:%S', errors='coerce').dt.strftime('%Y-%m-%d')
            # Eliminar filas donde la conversión de fecha resultó en NaT (Not a Time)
            df.dropna(subset=['marca_temporal'], inplace=True)
            print("-> Conversión completa.")

        print(f"-> Archivo CSV cargado con {len(df)} registros.")
    except Exception as e:
        print(f"Ocurrió un error al leer o procesar el archivo CSV: {e}")
        return

    # --- Paso 2: Conectarse a la base de datos ---
    try:
        conn = sqlite3.connect(DB_FILEPATH)
        cursor = conn.cursor()
        print(f"-> Conexión exitosa con la base de datos '{DB_FILEPATH}'.")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return

    # --- Paso 3: Borrar y crear la tabla ---
    try:
        # Borrar la tabla si ya existe para empezar de cero
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        print(f"-> Tabla '{TABLE_NAME}' anterior eliminada (si existía).")

        # Crear la tabla sin clave primaria
        column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
        create_table_query = f'CREATE TABLE {TABLE_NAME} ({column_definitions});'
        
        cursor.execute(create_table_query)
        print(f"-> Nueva tabla '{TABLE_NAME}' creada sin clave primaria.")

    except Exception as e:
        print(f"Error al recrear la tabla: {e}")
        conn.close()
        return

    # --- Paso 4: Insertar todos los datos ---
    registros = [tuple(x) for x in df.to_records(index=False)]
    column_names = ", ".join([f'"{col}"' for col in df.columns])
    placeholders = ", ".join(["?"] * len(df.columns))
    insert_query = f"INSERT INTO {TABLE_NAME} ({column_names}) VALUES ({placeholders});"

    try:
        cursor.executemany(insert_query, registros)
        conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        filas_insertadas = cursor.fetchone()[0]

        print(f"-> Se insertaron {filas_insertadas} registros en la tabla.")

    except Exception as e:
        print(f"Ocurrió un error durante la inserción de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de importación completado!")

if __name__ == '__main__':
    importar_documentacion_inscripciones()