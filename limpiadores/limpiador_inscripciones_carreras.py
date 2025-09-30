
import pandas as pd
import re
import os
import argparse

# --- Configuración de rutas relativas ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARRERAS_FILE = os.path.join(BASE_DIR, 'data', 'procesados', 'carreras.csv')

def limpiar_inscripciones_carreras(input_file, output_file, anio):
    """
    Procesa el reporte de inscripciones a carreras para un año específico.
    Extrae la carrera de los encabezados, normaliza los datos y los guarda en un CSV.
    """
    print(f"Iniciando el proceso de limpieza de inscripciones a carreras para el año {anio}...")

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

    # --- Paso 2: Procesar el archivo de inscripciones ---
    try:
        df_inscripciones = pd.read_excel(input_file, header=None)
        
        datos_limpios = []
        current_carrera_code = None

        print("-> Procesando filas del reporte de inscripciones a carreras...")
        for index, row in df_inscripciones.iterrows():
            cell_value = str(row.iloc[0])
            match = re.search(r'\((.*?)\)', cell_value)
            
            # Condición 1: La fila es un encabezado de carrera
            if match and match.group(1) in codigos_carrera_validos:
                current_carrera_code = match.group(1)
                continue

            # Condición 2: La fila es un encabezado de columnas. La detectamos y la saltamos.
            if 'Apellido y Nombre' in cell_value or 'N° Documento' in str(row.iloc[1]):
                continue

            # Condición 3: La fila es un dato de alumno
            if current_carrera_code and pd.notna(row.iloc[1]):
                datos_limpios.append({
                    'apellido_y_nombre': row.iloc[0],
                    'n_documento': row.iloc[1],
                    'plan': row.iloc[2],
                    'version': row.iloc[3],
                    'fecha_insc': row.iloc[4],
                    'fecha_ingreso': row.iloc[5],
                    'estado_insc': row.iloc[6],
                    'tipo_ingreso': row.iloc[7],
                    'modalidad': row.iloc[8],
                    'carrera': current_carrera_code,
                    'anio': anio
                })
        
        if not datos_limpios:
            print("Resultado: No se encontraron datos de inscripción a carrera válidos.")
            return

        # --- Paso 3: Eliminar duplicados y guardar los datos limpios ---
        df_limpio = pd.DataFrame(datos_limpios)

        # Convertir y estandarizar fechas a 'YYYY-MM-DD'
        df_limpio['fecha_insc'] = pd.to_datetime(df_limpio['fecha_insc'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
        df_limpio['fecha_ingreso'] = pd.to_datetime(df_limpio['fecha_ingreso'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Eliminar filas donde la conversión de fecha de inscripción falló
        df_limpio.dropna(subset=['fecha_insc'], inplace=True)

        # Eliminamos duplicados basados en la futura llave primaria
        df_limpio.drop_duplicates(subset=['n_documento', 'carrera'], inplace=True)
        print(f"-> Se eliminaron duplicados. Quedan {len(df_limpio)} registros únicos.")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df_limpio.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Proceso finalizado. Archivo limpio guardado como '{output_file}'.")

    except Exception as e:
        print(f"Error al procesar el archivo de inscripciones a carreras: {e}")
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Limpia los datos de inscripciones a carreras desde un archivo Excel.')
    parser.add_argument('--archivo-entrada', required=True, help='Ruta del archivo Excel de entrada.')
    parser.add_argument('--archivo-salida', required=True, help='Ruta del archivo CSV de salida.')
    parser.add_argument('--anio', required=True, type=int, help='Año de la inscripción a procesar.')
    
    args = parser.parse_args()
    
    limpiar_inscripciones_carreras(args.archivo_entrada, args.archivo_salida, args.anio)
