
import pandas as pd
import sqlite3
import os

# --- Configuración ---
CSV_INPUT_PATH = 'data/procesados/inscripciones_carreras_2025_procesado.csv'
DB_OUTPUT_PATH = 'data/base_de_datos/academica.db'
TABLE_NAME = 'inscripciones_carreras'

def importar_inscripciones_carreras():
    """
    Importa los datos de inscripciones a carreras desde un CSV a la base de datos SQLite.
    La tabla es eliminada y creada de nuevo en cada ejecución.
    """
    print(f"Iniciando la importación de '{CSV_INPUT_PATH}' a la tabla '{TABLE_NAME}'...")

    if not os.path.exists(CSV_INPUT_PATH):
        print(f"Error: No se encontró el archivo CSV en la ruta: {CSV_INPUT_PATH}")
        return

    # --- Paso 1: Leer el archivo CSV ---
    try:
        df = pd.read_csv(CSV_INPUT_PATH, encoding='utf-8')
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}")
        return

    # --- Paso 2: Conectarse a la base de datos ---
    try:
        conn = sqlite3.connect(DB_OUTPUT_PATH)
        cursor = conn.cursor()
        print(f"-> Conexión con la base de datos '{DB_OUTPUT_PATH}' establecida.")
    except Exception as e:
        print(f"Ocurrió un error al conectar con la base de datos: {e}")
        return

    # --- Paso 3: Eliminar y crear la tabla con llave primaria compuesta ---
    try:
        print(f"-> Eliminando la tabla '{TABLE_NAME}' si existe...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

        print(f"-> Creando la tabla '{TABLE_NAME}' con llave primaria (n_documento, carrera)...")
        column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
        
        create_table_query = f"""
        CREATE TABLE {TABLE_NAME} (
            {column_definitions},
            PRIMARY KEY (n_documento, carrera)
        );
        """
        cursor.execute(create_table_query)
        print(f"-> Tabla '{TABLE_NAME}' creada exitosamente.")

    except Exception as e:
        print(f"Ocurrió un error al recrear la tabla: {e}")
        conn.close()
        return
        
    # --- Paso 4: Insertar datos en la nueva tabla ---
    try:
        df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        print(f"-> Se insertaron {len(df)} registros en la tabla '{TABLE_NAME}'.")

    except Exception as e:
        print(f"Ocurrió un error durante la inserción de datos: {e}")
    finally:
        conn.commit()
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print(f"\n¡Proceso de importación de {TABLE_NAME} completado!")

if __name__ == '__main__':
    importar_inscripciones_carreras()
