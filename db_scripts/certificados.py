import pandas as pd
import sqlite3
import os
import re

def to_snake_case(name):
    """Convierte un string a formato snake_case."""
    # Reemplaza caracteres especiales y espacios con guiones bajos
    s1 = re.sub(r'[\síó]', lambda m: {' ':'_', 'í':'i', 'ó':'o'}[m.group(0)], name)
    # Convierte todo a minúsculas
    return s1.lower()

def importar_certificados_con_snake_case(csv_filepath, db_filepath, table_name='certificados'):
    """
    Limpia los nombres de las columnas a snake_case e importa los datos desde un
    archivo CSV a una tabla SQLite, controlando duplicados.
    """
    print(f"Iniciando la importación de '{csv_filepath}' a la tabla '{table_name}'...")

    # --- Paso 1: Leer y limpiar el archivo CSV ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        df.dropna(how='all', inplace=True)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")

        # --- Subpaso 1.1: Normalizar nombres de columnas a snake_case ---
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

    # --- Paso 3: Crear la tabla dinámicamente con los nombres correctos ---
    # Generamos la definición de las columnas para la consulta CREATE TABLE
    column_definitions = ", ".join([f'"{col}" TEXT' for col in df.columns if col != 'codigo'])
    
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        "codigo" TEXT PRIMARY KEY,
        {column_definitions}
    );
    """
    try:
        cursor.execute(create_table_query)
        print(f"-> Tabla '{table_name}' asegurada y lista para la inserción.")
    except Exception as e:
        print(f"Ocurrió un error al crear la tabla: {e}")
        conn.close()
        return
        
    # --- Paso 4: Insertar datos controlando duplicados ---
    registros_a_insertar = [tuple(x) for x in df.to_records(index=False)]
    
    # Generamos la consulta de inserción dinámicamente
    column_names_for_insert = ", ".join([f'"{col}"' for col in df.columns])
    placeholders = ", ".join(["?"] * len(df.columns))
    insert_query = f"INSERT OR IGNORE INTO {table_name} ({column_names_for_insert}) VALUES ({placeholders});"
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        filas_antes = cursor.fetchone()[0]

        cursor.executemany(insert_query, registros_a_insertar)
        conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        filas_despues = cursor.fetchone()[0]
        
        nuevos_registros = filas_despues - filas_antes
        duplicados_ignorados = len(df) - nuevos_registros
        
        print(f"-> Se insertaron {nuevos_registros} registros nuevos.")
        print(f"-> Se ignoraron {duplicados_ignorados} registros duplicados.")

    except Exception as e:
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de importación de certificados completado!")


if __name__ == '__main__':
    # --- Configuración ---
    csv_input_path = 'data/procesados/certificados.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    importar_certificados_con_snake_case(csv_input_path, db_output_path, 'certificados')

