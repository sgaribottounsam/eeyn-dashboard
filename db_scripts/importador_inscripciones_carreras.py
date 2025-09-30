
import pandas as pd
import sqlite3
import os
import argparse
import sys

# --- Configuración ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'base_de_datos', 'academica.db')
TABLE_NAME = 'inscripciones_carreras'

def importar_inscripciones_carreras(csv_input_path):
    """
    Importa los datos de inscripciones a carreras desde un CSV a la base de datos SQLite.
    Agrega nuevos registros a la tabla, ignorando duplicados basados en la llave primaria (nº_documento, propuesta).
    """
    print(f"Iniciando la importación de '{csv_input_path}' a la tabla '{TABLE_NAME}'...")

    if not os.path.exists(csv_input_path):
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_input_path}")
        sys.exit(1)

    # --- Paso 1: Leer el archivo CSV ---
    try:
        df = pd.read_csv(csv_input_path, encoding='utf-8')
        # Forzar todas las columnas a string para consistencia con la DB (TEXT)
        df = df.astype(str)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}")
        sys.exit(1)

    # --- Paso 2: Conectarse a la base de datos ---
    try:
        conn = sqlite3.connect(DB_OUTPUT_PATH)
        cursor = conn.cursor()
        print(f"-> Conexión con la base de datos '{DB_OUTPUT_PATH}' establecida.")
    except Exception as e:
        print(f"Ocurrió un error al conectar con la base de datos: {e}")
        sys.exit(1)

    # --- Paso 3: Crear la tabla si no existe con la nueva llave primaria ---
    try:
        print(f"-> Creando la tabla '{TABLE_NAME}' si no existe...")
        column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns])
        
        # Se usa "IF NOT EXISTS" para no fallar si la tabla ya está creada.
        # La llave primaria se define con 'nº_documento' y 'propuesta'.
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            {column_definitions},
            PRIMARY KEY ("n_documento", "carrera")
        );
        """
        cursor.execute(create_table_query)
        print(f"-> Tabla '{TABLE_NAME}' lista.")

    except Exception as e:
        print(f"Ocurrió un error al crear o verificar la tabla: {e}")
        conn.close()
        sys.exit(1)
        
    # --- Paso 4: Insertar datos ignorando duplicados ---
    try:
        # Se construye una sentencia INSERT OR IGNORE para evitar fallos por duplicados
        # y agregar únicamente los registros nuevos.
        cols = ', '.join([f'"{col}"' for col in df.columns])
        placeholders = ', '.join(['?'] * len(df.columns))
        sql = f"INSERT OR IGNORE INTO {TABLE_NAME} ({cols}) VALUES ({placeholders})"
        
        # Contar filas afectadas para reportar cuántos registros nuevos se agregaron
        initial_changes = conn.total_changes
        cursor.executemany(sql, df.to_records(index=False))
        final_changes = conn.total_changes
        
        inserted_rows = final_changes - initial_changes

        print(f"-> Se procesaron {len(df)} registros. Se insertaron {inserted_rows} nuevos registros en '{TABLE_NAME}'.")

    except Exception as e:
        print(f"Ocurrió un error durante la inserción de datos: {e}")
    finally:
        conn.commit()
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print(f"\n¡Proceso de importación de {TABLE_NAME} completado!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importa datos de inscripciones a carreras a la base de datos.')
    parser.add_argument('--archivo-csv', required=True, help='Ruta del archivo CSV a importar.')
    args = parser.parse_args()
    
    importar_inscripciones_carreras(args.archivo_csv)
