import pandas as pd
import re
import os
import argparse

# --- Configuración de rutas relativas ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARRERAS_FILE = os.path.join(BASE_DIR, 'data', 'procesados', 'carreras.csv')

def limpiar_preinscriptos(input_file, output_file, anio):
    """
    Procesa el reporte de preinscriptos a carreras para un año específico.
    Extrae la carrera de los encabezados, normaliza los datos y los guarda en un CSV.
    """
    print(f"Iniciando el proceso de limpieza de preinscriptos para el año {anio}...")

    if not all(os.path.exists(f) for f in [input_file, CARRERAS_FILE]):
        print(f"Error: No se encontró el archivo de entrada o de carreras.")
        print(f"Buscando: {input_file} y {CARRERAS_FILE}")
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
        df_preinscriptos = pd.read_excel(input_file, header=None)
        
        datos_limpios = []
        current_carrera_code = None

        print("-> Procesando filas del reporte de preinscriptos...")
        for index, row in df_preinscriptos.iterrows():
            cell_value = str(row.iloc[0])
            match = re.search(r'\((.*?)\)', cell_value)
            
            if match and match.group(1) in codigos_carrera_validos:
                current_carrera_code = match.group(1)
                continue

            if 'Apellido y Nombres' in cell_value or 'Identificación' in str(row.iloc[1]):
                continue

            if current_carrera_code and pd.notna(row.iloc[1]):
                # INDICES CORREGIDOS: Se asume que hay 2 columnas extra (ej. Sexo, Nacionalidad) no utilizadas
                # entre 'identificacion' (1) y 'email' (que ahora es el índice 4)
                datos_limpios.append({
                    'apellido_y_nombres': row.iloc[0],
                    'identificacion': row.iloc[1],
                    'email': row.iloc[4],      # Corregido
                    'telefono': row.iloc[5],    # Corregido
                    'colegio': row.iloc[6],     # Corregido
                    'estado': row.iloc[7],      # Corregido
                    'carrera': current_carrera_code,
                    'anio': anio
                })
        
        if not datos_limpios:
            print("Resultado: No se encontraron datos de preinscripción válidos.")
            return

        # --- Paso 3: Eliminar duplicados y guardar los datos limpios ---
        df_limpio = pd.DataFrame(datos_limpios)
        
        df_limpio.drop_duplicates(subset=['identificacion', 'carrera'], inplace=True)
        print(f"-> Se eliminaron duplicados. Quedan {len(df_limpio)} registros únicos.")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_limpio.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Proceso finalizado. Archivo limpio guardado como '{output_file}'.")

    except Exception as e:
        print(f"Error al procesar el archivo de preinscriptos: {e}")
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Limpia los datos de preinscriptos desde un archivo Excel.')
    parser.add_argument('--archivo-entrada', required=True, help='Ruta del archivo Excel de entrada.')
    parser.add_argument('--archivo-salida', required=True, help='Ruta del archivo CSV de salida.')
    parser.add_argument('--anio', required=True, type=int, help='Año de la preinscripción a procesar.')
    
    args = parser.parse_args()
    
    limpiar_preinscriptos(args.archivo_entrada, args.archivo_salida, args.anio)