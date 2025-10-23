
import pandas as pd
import sqlite3
import os

# --- Configuración ---
CSV_FILEPATH = 'data/procesados/CPU_procesados.csv'
DB_FILEPATH = 'data/base_de_datos/academica.db'
TABLE_NAME = 'aspirantes_test'
COLUMN_TO_TEST = 'ano_ingreso'

print(f"--- Test de Aislamiento para la columna '{COLUMN_TO_TEST}' ---")

# 1. Leer el archivo CSV
print(f"\n[Paso 1] Leyendo el archivo: {CSV_FILEPATH}")
try:
    df = pd.read_csv(CSV_FILEPATH, encoding='utf-8')
    print("-> Archivo CSV cargado con éxito.")
except Exception as e:
    print(f"Error al leer el CSV: {e}")
    exit()

# 2. Verificar el tipo de dato original
print(f"\n[Paso 2] Verificando el tipo de dato de '{COLUMN_TO_TEST}' antes de la conversión.")
if COLUMN_TO_TEST in df.columns:
    print(f"-> Tipo de dato (dtype) original: {df[COLUMN_TO_TEST].dtype}")
else:
    print(f"Error: La columna '{COLUMN_TO_TEST}' no se encontró en el CSV.")
    exit()

# 3. Realizar la conversión a tipo numérico
print(f"\n[Paso 3] Convirtiendo la columna '{COLUMN_TO_TEST}' a tipo numérico (entero).")
df[COLUMN_TO_TEST] = pd.to_numeric(df[COLUMN_TO_TEST], errors='coerce').fillna(0).astype(int)

# 4. Verificar el tipo de dato después de la conversión
print(f"\n[Paso 4] Verificando el tipo de dato después de la conversión.")
print(f"-> Tipo de dato (dtype) nuevo: {df[COLUMN_TO_TEST].dtype}")

# 5. Conectar a la base de datos e insertar en una tabla de prueba
print(f"\n[Paso 5] Insertando los datos en una tabla de prueba: '{TABLE_NAME}'")
try:
    conn = sqlite3.connect(DB_FILEPATH)
    cursor = conn.cursor()
    # Usamos una copia del dataframe para no afectar el original
    df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
    print("-> Datos insertados en la tabla de prueba.")
except Exception as e:
    print(f"Error durante la inserción a la base de datos: {e}")
    conn.close()
    exit()

# 6. Leer los datos de vuelta con pandas y verificar el tipo
print(f"\n[Paso 6] Leyendo los datos desde la tabla '{TABLE_NAME}' con pandas para verificar.")
df_from_db = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)

print("-> Tipos de datos leídos desde la base de datos con pandas:")
print(df_from_db.info())

# 7. Limpieza
print(f"\n[Paso 7] Limpiando la tabla de prueba.")
cursor.execute(f"DROP TABLE {TABLE_NAME}")
conn.commit()
conn.close()
print("-> Tabla de prueba eliminada. Test completado.")
