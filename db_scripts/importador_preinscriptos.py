import pandas as pd
import sqlite3
import os
import argparse
import sys

# --- Configuración ---
DB_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'base_de_datos', 'academica.db')
TABLE_NAME = 'preinscriptos'

def importar_preinscriptos(csv_input_path):
    """
    Importa datos de preinscriptos desde un CSV a SQLite.
    Crea la tabla si no existe, agrega columnas si es necesario,
    y borra los datos del año a importar antes de la inserción para evitar duplicados.
    """
    print(f"Iniciando la importación de '{csv_input_path}' a la tabla '{TABLE_NAME}'...")

    if not os.path.exists(csv_input_path):
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(csv_input_path, encoding='utf-8')
        df = df.astype(str)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if 'anio' not in df.columns or df['anio'].nunique() != 1:
        print("Error: El CSV debe contener una columna 'anio' con un único valor.", file=sys.stderr)
        sys.exit(1)
    
    anio_a_importar = df['anio'].iloc[0]
    print(f"-> Año a importar detectado: {anio_a_importar}")

    try:
        conn = sqlite3.connect(DB_OUTPUT_PATH)
        cursor = conn.cursor()
        print(f"-> Conexión con la base de datos '{DB_OUTPUT_PATH}' establecida.")

        # --- Sincronizar esquema de la tabla (Añadir columnas si es necesario) ---
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        table_columns = {row[1] for row in cursor.fetchall()}
        
        if not table_columns:
            print(f"-> La tabla '{TABLE_NAME}' no existe. Se creará.")
            column_definitions = ", ".join([f'\"{col}\" TEXT' for col in df.columns])
            # Asumimos que las columnas de la PK existen y tienen el nombre normalizado
            pk_cols = ['identificacion', 'carrera']
            if all(c in df.columns for c in pk_cols):
                create_query = f"CREATE TABLE {TABLE_NAME} ({column_definitions}, PRIMARY KEY ({', '.join(pk_cols)}))"
                cursor.execute(create_query)
                print(f"-> Tabla '{TABLE_NAME}' creada con llave primaria.")
            else:
                print(f"Error: Faltan columnas para la llave primaria ({', '.join(pk_cols)}) en el CSV.", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"-> La tabla '{TABLE_NAME}' ya existe. Verificando columnas...")
            csv_columns = set(df.columns)
            missing_columns = csv_columns - table_columns
            if missing_columns:
                print(f"  -> Columnas faltantes en la tabla: {missing_columns}. Añadiéndolas...")
                for col in missing_columns:
                    cursor.execute(f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{col}" TEXT')
                print("  -> Columnas añadidas exitosamente.")
            else:
                print("  -> El esquema de la tabla está actualizado.")

        # --- Borrar registros del año a importar para evitar duplicados ---
        print(f"-> Borrando registros existentes para el año {anio_a_importar}...")
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE anio = ?", (anio_a_importar,))
        print(f"  -> Se eliminaron {cursor.rowcount} registros antiguos.")

        # --- Insertar datos ---
        df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        print(f"-> Se insertaron {len(df)} registros nuevos para el año {anio_a_importar}.")

        conn.commit()
        print("\n¡Proceso de importación completado!")

    except Exception as e:
        print(f"Ocurrió un error durante la operación de base de datos: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("-> Conexión con la base de datos cerrada.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Importa datos de preinscripciones a la base de datos de forma segura.')
    parser.add_argument('--archivo-csv', required=True, help='Ruta del archivo CSV procesado a importar.')
    args = parser.parse_args()
    importar_preinscriptos(args.archivo_csv)
