import pandas as pd
import sqlite3
import os

def importar_carreras_sin_repetir(csv_filepath, db_filepath, table_name='carreras'):
    """
    Crea una tabla de carreras (si no existe) con 'Codigo' como llave primaria
    e importa los datos desde un archivo CSV, ignorando registros que ya existan.

    Args:
        csv_filepath (str): Ruta al archivo CSV con los datos de las carreras.
        db_filepath (str): Ruta a la base de datos SQLite.
        table_name (str): Nombre de la tabla de carreras.
    """
    print(f"Iniciando la importación de '{csv_filepath}' a la tabla '{table_name}'...")

    # --- Paso 1: Leer el archivo CSV ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        df.dropna(how='all', inplace=True)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_filepath}")
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}")
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
    # La llave primaria en 'Codigo' asegura que cada carrera sea única.
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        "Codigo" TEXT PRIMARY KEY,
        "Nombre" TEXT,
        "Tipo" TEXT,
        "Estado" TEXT
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
    registros_a_insertar = [tuple(x) for x in df.to_numpy()]
    
    insert_query = f"""
    INSERT OR IGNORE INTO {table_name} ("Codigo", "Nombre", "Tipo", "Estado") 
    VALUES (?, ?, ?, ?);
    """
    
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
        print(f"-> Se ignoraron {duplicados_ignorados} registros duplicados (ya existentes).")

    except Exception as e:
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de importación de carreras completado!")


if __name__ == '__main__':
    # --- Configuración ---
    # Se asume que este script se ejecuta desde la carpeta raíz del proyecto.
    # Ejemplo de ejecución desde la raíz: python db_scripts/importador_carreras.py
    
    csv_input_path = 'data/procesados/carreras.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    importar_carreras_sin_repetir(csv_input_path, db_output_path, 'certificados')