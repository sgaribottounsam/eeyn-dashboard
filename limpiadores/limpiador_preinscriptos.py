import pandas as pd
import re
import os
import argparse
import unicodedata

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to underscores.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def limpiar_preinscriptos(input_file, output_file, anio):
    """
    Procesa el reporte de preinscriptos a carreras para un año específico.
    Extrae la carrera de los encabezados, normaliza los datos y todas las columnas,
    y los guarda en un CSV.
    """
    print(f"Iniciando el proceso de limpieza de preinscriptos para el año {anio}...")

    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo de entrada: {input_file}")
        return

    try:
        df_raw = pd.read_excel(input_file, header=None)
        
        all_data = []
        current_carrera_code = None
        header_list = []

        print("-> Procesando filas del reporte de preinscriptos...")
        for index, row in df_raw.iterrows():
            # Fila de Carrera: Busca un código entre paréntesis, ej: (CP-CCCP-PC)
            cell_value = str(row.iloc[0])
            match = re.search(r'\((.*?)\)', cell_value)
            
            if match:
                # Extrae el código de la carrera y lo almacena
                current_carrera_code = match.group(1)
                print(f"  -> Detectada carrera: {current_carrera_code}")
                continue

            # Fila de Encabezado: Busca la fila que contiene los títulos de las columnas
            if 'Apellido y Nombres' in cell_value:
                header_list = [slugify(str(col)) for col in row if pd.notna(col)]
                print(f"  -> Encabezados de datos identificados: {header_list}")
                continue

            # Si no tenemos carrera o encabezados, o la fila es inválida, la saltamos
            if not current_carrera_code or not header_list or pd.isna(row.iloc[1]):
                continue

            # Fila de Datos: Procesar datos del estudiante
            row_data = {header_list[i]: val for i, val in enumerate(row) if i < len(header_list)}
            row_data['carrera'] = current_carrera_code
            row_data['anio'] = anio
            all_data.append(row_data)
        
        if not all_data:
            print("Resultado: No se encontraron datos de preinscripción válidos.")
            return

        # --- Crear y limpiar el DataFrame final ---
        df_limpio = pd.DataFrame(all_data)
        
        # Asegurarse que la columna 'identificacion' existe antes de usarla
        if 'identificacion' in df_limpio.columns:
            df_limpio.drop_duplicates(subset=['identificacion', 'carrera'], inplace=True)
            print(f"-> Se eliminaron duplicados. Quedan {len(df_limpio)} registros únicos.")
        else:
            print("Advertencia: No se encontró la columna 'identificacion'. No se pudieron eliminar duplicados.")

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
