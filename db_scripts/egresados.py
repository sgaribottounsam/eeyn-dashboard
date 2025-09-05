import pandas as pd
import sqlite3
import os

def importar_egresados_sin_repetir(csv_filepath, db_filepath, table_name='egresados'):
    """
    Crea una tabla de egresados (si no existe) con una llave primaria para evitar duplicados
    e importa los datos desde un archivo CSV, ignorando registros que ya existan.

    Args:
        csv_filepath (str): Ruta al archivo CSV con los datos de egresados.
        db_filepath (str): Ruta a la base de datos SQLite.
        table_name (str): Nombre de la tabla de egresados.
    """
    print(f"Iniciando la importación de '{csv_filepath}' a la tabla '{table_name}'...")

    # --- Paso 1: Leer el archivo CSV ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        # Limpieza básica: eliminar filas completamente vacías si las hubiera
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
    # La llave primaria en (Documento, Propuesta, Plan) asegura que no haya
    # registros duplicados para el mismo egreso de una persona.
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        "Apellido y Nombres" TEXT,
        "Documento" TEXT,
        "Legajo" TEXT,
        "Inscripción" TEXT,
        "Ingreso" TEXT,
        "Egreso" TEXT,
        "Certificado" TEXT,
        "Propuesta" TEXT,
        "Plan" TEXT,
        PRIMARY KEY ("Documento", "Propuesta", "Plan")
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
    # Convertimos el DataFrame a una lista de tuplas para la inserción
    registros_a_insertar = [tuple(x) for x in df.to_numpy()]
    
    # Preparamos la consulta de inserción
    # INSERT OR IGNORE es la clave: si un registro viola la PRIMARY KEY, se ignora.
    insert_query = f"""
    INSERT OR IGNORE INTO {table_name} 
    ("Apellido y Nombres", "Documento", "Legajo", "Inscripción", "Ingreso", "Egreso", "Certificado", "Propuesta", "Plan") 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    try:
        # Obtenemos la cantidad de filas antes de la inserción
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        filas_antes = cursor.fetchone()[0]

        # Ejecutamos la inserción para todos los registros a la vez
        cursor.executemany(insert_query, registros_a_insertar)
        conn.commit() # Guardamos los cambios en la base de datos

        # Obtenemos la cantidad de filas después de la inserción
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

    print("\n¡Proceso de importación de egresados completado!")


if __name__ == '__main__':
    # --- Configuración ---
    # Asume que este script está en 'db_scripts/' y los datos en 'data/procesados/'
    
    csv_input_path = 'data/procesados/Egresados_todos.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    importar_egresados_sin_repetir(csv_input_path, db_output_path, 'egresados')