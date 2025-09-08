import pandas as pd
import sqlite3
import os
import re

def to_snake_case(name):
    """Convierte un string a formato snake_case."""
    name = name.strip()
    s1 = re.sub(r'[\s]+', '_', name)
    return s1.lower()

def importar_planes(csv_filepath, db_filepath, table_name='planes', strategy='REPLACE'):
    """
    Normaliza los nombres de las columnas e importa los datos de los planes de estudio
    desde un archivo CSV a una tabla SQLite, controlando duplicados.

    Args:
        csv_filepath (str): Ruta al archivo CSV.
        db_filepath (str): Ruta a la base de datos SQLite.
        table_name (str): Nombre de la tabla.
        strategy (str): 'REPLACE' para actualizar o 'IGNORE' para mantener existentes.
    """
    print(f"Iniciando la importación a la tabla '{table_name}' con la estrategia '{strategy}'...")

    # --- Paso 1: Leer y limpiar el archivo CSV ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        df.dropna(how='all', inplace=True)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")

        df.columns = [to_snake_case(col) for col in df.columns]
        print("-> Columnas normalizadas a formato snake_case:")
        print(list(df.columns))

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_filepath}")
        return
    except Exception as e:
        print(f"Ocurrió un error al procesar el DataFrame: {e}")
        return

    # --- Paso 2: Conectarse a la base de datos ---
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        print(f"-> Conexión con la base de datos '{db_filepath}' establecida.")
    except Exception as e:
        print(f"Ocurrió un error al conectar con la base de datos: {e}")
        return

    # --- Paso 3: Crear la tabla con LLAVE PRIMARIA ---
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        propuesta TEXT,
        plan TEXT,
        actualizado TEXT,
        nombre_largo TEXT,
        total_materias INTEGER,
        PRIMARY KEY (propuesta, plan)
    );
    """
    try:
        cursor.execute(create_table_query)
        print(f"-> Tabla '{table_name}' asegurada y lista para la inserción.")
    except Exception as e:
        print(f"Ocurrió un error al crear la tabla: {e}")
        conn.close()
        return
        
    # --- Paso 4: Insertar datos con la estrategia elegida ---
    registros_a_insertar = [tuple(x) for x in df.to_records(index=False)]
    
    column_names = ", ".join([f'"{col}"' for col in df.columns])
    placeholders = ", ".join(["?"] * len(df.columns))
    
    # Usamos la estrategia elegida en la consulta SQL
    insert_query = f"INSERT OR {strategy} INTO {table_name} ({column_names}) VALUES ({placeholders});"
    
    try:
        conn.execute("BEGIN TRANSACTION")
        initial_changes = conn.total_changes
        
        cursor.executemany(insert_query, registros_a_insertar)
        
        conn.commit()
        final_changes = conn.total_changes
        
        registros_afectados = final_changes - initial_changes
        
        if strategy == 'REPLACE':
            print(f"-> Se insertaron o reemplazaron {registros_afectados} registros.")
        else: # IGNORE
             print(f"-> Se insertaron {registros_afectados} registros nuevos.")
             print(f"-> Se ignoraron {len(df) - registros_afectados} registros duplicados.")

    except Exception as e:
        conn.rollback()
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print(f"\n¡Proceso de importación para la tabla '{table_name}' completado!")


if __name__ == '__main__':
    # --- Configuración ---
    csv_input_path = 'data/procesados/planes.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    # Aquí elegís la estrategia. Para este caso, usamos 'REPLACE'.
    importar_planes(csv_input_path, db_output_path, strategy='REPLACE')

