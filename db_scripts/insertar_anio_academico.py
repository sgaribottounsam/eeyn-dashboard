import sqlite3
import os

def poblar_anio_academico(start_year, end_year, db_filepath, table_name='anio_academico'):
    """
    Genera los años académicos y los inserta directamente en la base de datos,
    creando la tabla si es necesario y evitando duplicados.

    Args:
        start_year (int): El primer año a generar.
        end_year (int): El último año a generar.
        db_filepath (str): Ruta a la base de datos SQLite.
        table_name (str): Nombre de la tabla de años.
    """
    print(f"Iniciando la carga de datos en la tabla '{table_name}'...")

    # --- Paso 1: Generar los datos en memoria ---
    anios_data = []
    for anio in range(start_year, end_year + 1):
        inicio = f"1/4/{anio}"
        fin = f"31/3/{anio + 1}"
        anios_data.append((anio, inicio, fin))
    
    print(f"-> Se generaron {len(anios_data)} registros de años académicos en memoria.")

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
        "anio" INTEGER PRIMARY KEY,
        "inicio" TEXT NOT NULL,
        "fin" TEXT NOT NULL
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
    insert_query = f"""
    INSERT OR IGNORE INTO {table_name} ("anio", "inicio", "fin") 
    VALUES (?, ?, ?);
    """
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        filas_antes = cursor.fetchone()[0]

        cursor.executemany(insert_query, anios_data)
        conn.commit()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        filas_despues = cursor.fetchone()[0]
        
        nuevos_registros = filas_despues - filas_antes
        duplicados_ignorados = len(anios_data) - nuevos_registros
        
        print(f"-> Se insertaron {nuevos_registros} registros nuevos.")
        print(f"-> Se ignoraron {duplicados_ignorados} registros duplicados (ya existentes).")

    except Exception as e:
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de carga de años académicos completado!")

    

db_output_path = 'data/base_de_datos/academica.db'  
poblar_anio_academico(1994, 2050, db_output_path, 'anio_academico')   
