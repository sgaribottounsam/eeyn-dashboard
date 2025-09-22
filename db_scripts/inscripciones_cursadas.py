import pandas as pd
import sqlite3
import os
import re

def to_snake_case(name):
    """Convierte un string a formato snake_case, manejando acentos y caracteres comunes."""
    name = str(name).strip()
    # CORRECCIÓN: Se quita el punto (.) de este regex para que no lo reemplace por un guion bajo.
    name = re.sub(r'[\s\/]+', '_', name)
    name = re.sub(r'[ÁÉÍÓÚáéíóú]', lambda m: {'Á':'a','É':'e','Í':'i','Ó':'o','Ú':'u','á':'a','é':'e','í':'i','ó':'o','ú':'u'}[m.group(0)], name)
    # Este regex se encargará de eliminar los puntos y otros caracteres no deseados.
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    return name.lower()

def importar_inscripciones(csv_filepath, db_filepath, table_name='inscripciones_cursadas', strategy='REPLACE'):
    """
    Limpia los datos de inscripciones (renombra columnas, convierte fechas) y los importa
    a una tabla SQLite, usando una estrategia de reemplazo para actualizaciones.
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
        
        # --- Subpaso 1.2: Convertir fecha a formato YYYY-MM-DD o NULL ---
        if 'fecha_inscripcion' in df.columns:
            # pd.to_datetime convierte las fechas. `errors='coerce'` transforma las que fallan en NaT (Not a Time)
            df['fecha_inscripcion'] = pd.to_datetime(df['fecha_inscripcion'], errors='coerce')
            # strftime convierte las fechas válidas a string 'YYYY-MM-DD'. NaT se convierte en None (NULL en SQL).
            df['fecha_inscripcion'] = df['fecha_inscripcion'].dt.strftime('%Y-%m-%d')
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

    # --- Paso 3: Crear la tabla con llave primaria ---
    # Una inscripción única se define por la persona, la comisión, la carrera y el período.
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        alumno TEXT,
        identificacion TEXT,
        comision TEXT,
        estado_insc TEXT,
        fecha_inscripcion DATE,
        carrera TEXT,
        periodo TEXT,
        PRIMARY KEY (identificacion, comision, carrera, periodo)
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
    
    insert_query = f"INSERT OR {strategy} INTO {table_name} ({column_names}) VALUES ({placeholders});"
    
    try:
        conn.execute("BEGIN TRANSACTION")
        initial_changes = conn.total_changes
        cursor.executemany(insert_query, registros_a_insertar)
        conn.commit()
        final_changes = conn.total_changes
        
        registros_afectados = final_changes - initial_changes
        print(f"-> Se insertaron o reemplazaron {registros_afectados} registros.")

    except Exception as e:
        conn.rollback()
        print(f"Ocurrió un error durante la importación de datos: {e}")
    finally:
        conn.close()
        print("-> Conexión con la base de datos cerrada.")

    print(f"\n¡Proceso de importación para la tabla '{table_name}' completado!")

if __name__ == '__main__':
    csv_input_path = 'data/procesados/inscripciones_procesado.csv'
    db_output_path = 'data/base_de_datos/academica.db'
    
    importar_inscripciones(csv_input_path, db_output_path, strategy='REPLACE')

