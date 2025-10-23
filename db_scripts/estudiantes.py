import pandas as pd
import sqlite3
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.text_utils import to_snake_case
def importar_estudiantes(csv_filepath, db_filepath, table_name):
    """
    Importa datos de estudiantes desde un CSV (con columnas ya en snake_case)
    a una tabla SQLite. Si un registro ya existe (basado en la llave primaria),
    lo reemplaza con la nueva versión.
    """
    print(f"Iniciando la importación de '{csv_filepath}' a la tabla '{table_name}'...")

    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        df.dropna(how='all', inplace=True)
        # --- FIX: Convertir explicitamente la columna 'ano_ingreso' a entero ---
        if 'ano_ingreso' in df.columns:
            df['ano_ingreso'] = pd.to_numeric(df['ano_ingreso'], errors='coerce').fillna(0).astype(int)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_filepath}")
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}")
        return

    # El CSV ya debería tener los nombres en snake_case gracias al limpiador,
    # pero aplicamos la función de nuevo como medida de seguridad.
    df.columns = [to_snake_case(col) for col in df.columns]

    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        print(f"-> Conexión con la base de datos '{db_filepath}' establecida.")
    except Exception as e:
        print(f"Ocurrió un error al conectar con la base de datos: {e}")
        return

    # --- CAMBIO 1: La PRIMARY KEY ahora es (tipo_y_no_documento, carrera) ---
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        apellido_y_nombre TEXT,
        tipo_y_n_documento TEXT,
        fecha_de_nacimiento TEXT,
        email TEXT,
        telefono TEXT,
        legajo TEXT,
        plan TEXT,
        ano_ingreso INTEGER,
        fecha_ingreso TEXT,
        ultimo_examen TEXT,
        ultima_reinscripcion TEXT,
        prom_con_aplazos REAL,
        prom_sin_aplazos REAL,
        actividades_aprobadas INTEGER,
        total_actividades INTEGER,
        estado_inscripcion TEXT,
        carrera TEXT,
        PRIMARY KEY (tipo_y_n_documento, carrera)
    );
    """
    try:
        cursor.execute(create_table_query)
        print(f"-> Tabla '{table_name}' asegurada y lista para la inserción.")
    except Exception as e:
        print(f"Ocurrió un error al crear la tabla: {e}")
        conn.close()
        return
        
    registros_a_insertar = list(df.itertuples(index=False, name=None))
    
    column_names = ", ".join([f'"{col}"' for col in df.columns])
    placeholders = ", ".join(["?"] * len(df.columns))
    
    # --- CAMBIO 2: Usamos INSERT OR REPLACE para actualizar registros existentes ---
    insert_query = f"INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES ({placeholders});"
    
    try:
        # Contamos los cambios (inserciones + actualizaciones) para dar un reporte más preciso
        conn.execute("BEGIN TRANSACTION")
        initial_changes = conn.total_changes
        
        cursor.executemany(insert_query, registros_a_insertar)
        
        conn.commit()
        final_changes = conn.total_changes
        
        registros_afectados = final_changes - initial_changes
        
        print(f"-> Se insertaron o actualizaron {registros_afectados} registros.")
        print(f"-> {len(df) - registros_afectados} registros no sufrieron cambios (eran idénticos).")

    except Exception as e:
        conn.rollback()
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print(f"\n¡Proceso de importación para la tabla '{table_name}' completado!")

if __name__ == '__main__':
    # --- Procesamiento en Lote ---
    # Se procesan ambas tablas, aspirantes y estudiantes, una después de la otra.
    
    configs = [
        {
            'csv_input_path': 'data/procesados/CPU_procesados.csv',
            'db_output_path': 'data/base_de_datos/academica.db',
            'table': 'aspirantes'
        },
        {
            'csv_input_path': 'data/procesados/Grado_pregrado_procesado.csv',
            'db_output_path': 'data/base_de_datos/academica.db',
            'table': 'estudiantes'
        }
    ]
    
    for config in configs:
        print(f"\n--- Iniciando para la tabla: {config['table']} ---")
        importar_estudiantes(config['csv_input_path'], config['db_output_path'], config['table'])

