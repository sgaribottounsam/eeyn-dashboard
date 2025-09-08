import pandas as pd
import sqlite3
import os

def clean_and_import_egresados(csv_filepath, db_filepath, table_name='egresados'):
    """
    Limpia los datos de egresados (renombra columnas, convierte fechas) y los importa
    a una tabla SQLite, controlando duplicados con una llave primaria.
    """
    print(f"Iniciando la importación y limpieza desde '{csv_filepath}'...")

    # --- Paso 1: Leer y limpiar el archivo CSV con pandas ---
    try:
        df = pd.read_csv(csv_filepath, encoding='utf-8')
        df.dropna(how='all', inplace=True)
        print(f"-> Archivo CSV cargado. Se encontraron {len(df)} registros.")

        # --- Subpaso 1.1: Renombrar columnas a formato snake_case ---
        nuevos_nombres = {
            'Apellido y Nombres': 'apellido_y_nombres',
            'Documento': 'documento',
            'Legajo': 'legajo',
            'Inscripción': 'fecha_inscripcion',
            'Ingreso': 'fecha_ingreso',
            'Egreso': 'fecha_egreso',
            'Certificado': 'certificado',
            'Propuesta': 'propuesta',
            'Plan': 'plan'
        }
        df.rename(columns=nuevos_nombres, inplace=True)
        print("-> Columnas renombradas a formato estándar.")

        # --- Subpaso 1.2: Convertir fechas a formato YYYY-MM-DD o NULL ---
        columnas_fecha = ['fecha_inscripcion', 'fecha_ingreso', 'fecha_egreso']
        for col in columnas_fecha:
            # pd.to_datetime convierte las fechas. `errors='coerce'` transforma las que fallan en NaT (Not a Time)
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
            # strftime convierte las fechas válidas a string 'YYYY-MM-DD'. NaT se convierte en None (NULL en SQL).
            df[col] = df[col].dt.strftime('%Y-%m-%d')
        print("-> Fechas procesadas. Las fechas inválidas o vacías se convertirán en NULL.")

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

    # --- Paso 3: Crear la tabla con nuevos nombres y tipos de datos ---
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        apellido_y_nombres TEXT,
        documento TEXT,
        legajo TEXT,
        fecha_inscripcion DATE,
        fecha_ingreso DATE,
        fecha_egreso DATE,
        certificado TEXT,
        propuesta TEXT,
        plan TEXT,
        PRIMARY KEY (documento, propuesta, plan)
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
    
    insert_query = f"""
    INSERT OR IGNORE INTO {table_name} 
    (apellido_y_nombres, documento, legajo, fecha_inscripcion, fecha_ingreso, fecha_egreso, certificado, propuesta, plan) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
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
        print(f"-> Se ignoraron {duplicados_ignorados} registros duplicados.")
    except Exception as e:
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print("\n¡Proceso de importación de egresados completado!")


if __name__ == '__main__':
    # --- Configuración ---
    csv_input_path = 'data/procesados/Egresados_todos.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    clean_and_import_egresados(csv_input_path, db_output_path, 'egresados')

