
import pandas as pd
import re
import os

# --- Configuración del script ---
INPUT_FILE = 'data/crudos/reporte de preinscriptos 2025.xlsx'
OUTPUT_FILE = 'data/procesados/preinscriptos_2025_procesado.csv'
CARRERAS_FILE = 'data/procesados/carreras.csv'

def limpiar_preinscriptos():
    """
    Procesa el reporte de preinscriptos a carreras para el año 2025.
    Extrae la carrera de los encabezados, normaliza los datos y los guarda en un CSV.
    """
    print("Iniciando el proceso de limpieza de preinscriptos 2025...")

    if not all(os.path.exists(f) for f in [INPUT_FILE, CARRERAS_FILE]):
        print(f"Error: No se encontró el archivo de entrada o de carreras.")
        print(f"Buscando: {INPUT_FILE} y {CARRERAS_FILE}")
        return

    # --- Paso 1: Leer códigos de carrera válidos ---
    try:
        df_carreras = pd.read_csv(CARRERAS_FILE, encoding='utf-8')
        codigos_carrera_validos = set(df_carreras['Codigo'])
        print(f"-> Se cargaron {len(codigos_carrera_validos)} códigos de carrera válidos.")
    except Exception as e:
        print(f"Error al leer el archivo de carreras: {e}")
        return

    # --- Paso 2: Procesar el archivo de preinscriptos ---
    try:
        df_preinscriptos = pd.read_excel(INPUT_FILE, header=None)
        
        datos_limpios = []
        current_carrera_code = None

        print("-> Procesando filas del reporte de preinscriptos...")
        for index, row in df_preinscriptos.iterrows():
            cell_value = str(row.iloc[0])
            match = re.search(r'\((.*?)\)', cell_value)
            
            # Condición 1: La fila es un encabezado de carrera
            if match and match.group(1) in codigos_carrera_validos:
                current_carrera_code = match.group(1)
                continue

            # Condición 2: La fila es un encabezado de columnas. La detectamos y la saltamos.
            if 'Apellido y Nombres' in cell_value or 'Identificación' in str(row.iloc[1]):
                continue

            # Condición 3: La fila es un dato de alumno
            if current_carrera_code and pd.notna(row.iloc[1]):
                datos_limpios.append({
                    'apellido_y_nombres': row.iloc[0],
                    'identificacion': row.iloc[1],
                    'email': row.iloc[2],
                    'telefono': row.iloc[3],
                    'colegio': row.iloc[4],
                    'estado': row.iloc[5],
                    'carrera': current_carrera_code,
                    'anio': 2025
                })
        
        if not datos_limpios:
            print("Resultado: No se encontraron datos de preinscripción válidos.")
            return

        # --- Paso 3: Eliminar duplicados y guardar los datos limpios ---
        df_limpio = pd.DataFrame(datos_limpios)
        
        # Eliminamos duplicados basados en la futura llave primaria
        df_limpio.drop_duplicates(subset=['identificacion', 'carrera'], inplace=True)
        print(f"-> Se eliminaron duplicados. Quedan {len(df_limpio)} registros únicos.")

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df_limpio.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"Proceso finalizado. Archivo limpio guardado como '{OUTPUT_FILE}'.")

    except Exception as e:
        print(f"Error al procesar el archivo de preinscriptos: {e}")
        return

if __name__ == '__main__':
    limpiar_preinscriptos()
