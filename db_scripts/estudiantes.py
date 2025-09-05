import pandas as pd
import sqlite3
import os

def crear_e_importar_alumnos(csv_filepath, db_filepath, table_name='estudiantes'):
    """
    Crea una tabla en una base de datos SQLite y la puebla con datos de un archivo CSV.
    Si la tabla ya existe, la elimina y la vuelve a crear para asegurar datos frescos.

    Args:
        csv_filepath (str): Ruta al archivo CSV con los datos limpios.
        db_filepath (str): Ruta a la base de datos SQLite que se creará o usará.
        table_name (str): Nombre de la tabla que se creará.
    """
    print(f"Iniciando la importación de '{csv_filepath}' a la tabla '{table_name}' en '{db_filepath}'...")

    # --- Paso 1: Leer el archivo CSV con pandas ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        print(f"-> Archivo CSV cargado correctamente con {len(df)} filas.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV en la ruta: {csv_filepath}")
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el CSV: {e}")
        return

    # --- Paso 2: Conectarse a la base de datos SQLite ---
    try:
        # La conexión crea el archivo .db si no existe
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()
        print("-> Conexión con la base de datos SQLite establecida.")
    except Exception as e:
        print(f"Ocurrió un error al conectar con la base de datos: {e}")
        return

    # --- Paso 3: Crear la tabla ---
    # Se define la estructura de la tabla con los tipos de datos de SQL.
    # Usamos TEXT para la mayoría de los campos por flexibilidad, INTEGER para números enteros y REAL para promedios.
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        "Apellido y Nombre" TEXT,
        "Tipo y N° Documento" TEXT,
        "Fecha de Nacimiento" TEXT,
        "Email" TEXT,
        "Teléfono" TEXT,
        "Legajo" TEXT,
        "Plan" TEXT,
        "Año Ingreso" INTEGER,
        "Fecha Ingreso" TEXT,
        "Último Examen" TEXT,
        "Última Reinscripción" TEXT,
        "Prom. con Aplazos" REAL,
        "Prom. sin Aplazos" REAL,
        "Actividades Aprobadas" INTEGER,
        "Total Actividades" INTEGER,
        "Estado inscripción" TEXT,
        "Carrera" TEXT
    );
    """
    
    try:
        # Eliminamos la tabla si ya existe para evitar datos duplicados o viejos
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        # Creamos la tabla nueva
        cursor.execute(create_table_query)
        print(f"-> Tabla '{table_name}' creada (o reiniciada) exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error al crear la tabla: {e}")
        conn.close()
        return
        
    # --- Paso 4: Importar los datos del DataFrame a la tabla SQL ---
    try:
        # La función to_sql de pandas es la forma más eficiente de hacer esto
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"-> Se importaron {len(df)} registros a la tabla '{table_name}'.")
    except Exception as e:
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        # Cerramos la conexión a la base de datos
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de importación a la base de datos completado!")

if __name__ == '__main__':
    # --- Configuración ---
    # Asume que este script está en una carpeta y 'data' está al mismo nivel.
    # ej: MI_PROYECTO/
    #     ├── data/
    #     │   └── Grado_pregrado_procesado.csv
    #     └── database_scripts/
    #         └── importador_db.py (este script)
    
    #csv_input_path = 'data/procesados/Grado_pregrado_procesado.csv'
    #db_output_path = 'data/base_de_datos/academica.db' # El archivo de la base de datos
    
    csv_input_path = 'data/procesados/CPU_procesados.csv'
    db_output_path = 'data/base_de_datos/academicas.db' # El archivo de la base de datos
    
    crear_e_importar_alumnos(csv_input_path, db_output_path, 'aspirantes')
