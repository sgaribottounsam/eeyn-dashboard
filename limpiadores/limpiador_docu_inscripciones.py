import pandas as pd
import os
import re

# --- Configuración de archivos ---
INPUT_FILE = 'data/crudos/Inscripción ingresantes CPU 1ºC 2026 (respuestas) - Respuestas de formulario 1.csv'
OUTPUT_FILE = 'data/procesados/inscripciones_docu_limpio.csv'

def limpiar_nombres_columnas(df):
    """
    Normaliza los nombres de las columnas de un DataFrame:
    - Convierte a minúsculas.
    - Reemplaza espacios y caracteres especiales por guiones bajos.
    - Elimina acentos y otros caracteres no estándar.
    """
    nuevos_nombres = []
    for col in df.columns:
        # Convertir a minúsculas y reemplazar espacios
        nombre = col.lower().strip().replace(' ', '_')
        # Quitar caracteres especiales y acentos
        nombre = re.sub(r'[^a-z0-9_]', '', nombre)
        nuevos_nombres.append(nombre)
    df.columns = nuevos_nombres
    return df

def procesar_inscripciones_documentacion():
    """
    Lee el archivo de inscripciones, limpia los datos y lo guarda en un nuevo CSV.
    """
    print(f"Iniciando la limpieza del archivo: {INPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        print(f"Error: El archivo de entrada no se encuentra en {INPUT_FILE}")
        return

    try:
        # --- Paso 1: Leer el archivo CSV ---
        df = pd.read_csv(INPUT_FILE)
        print(f"-> Se leyeron {len(df)} filas.")

        # --- Paso 2: Limpiar los nombres de las columnas ---
        df = limpiar_nombres_columnas(df)
        print("-> Nombres de columnas normalizados.")
        print("Nuevas columnas:", df.columns.tolist())

        # --- Paso 3: Guardar el archivo procesado ---
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        
        print(f"\nProceso finalizado. Archivo limpio guardado en: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Ocurrió un error durante el procesamiento: {e}")

if __name__ == '__main__':
    procesar_inscripciones_documentacion()
