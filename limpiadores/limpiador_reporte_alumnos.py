import pandas as pd
import os
import re

def to_snake_case(name):
    """Convierte un string a formato snake_case, manejando acentos y caracteres comunes."""
    name = name.strip()
    name = re.sub(r'[\s\.\/]+', '_', name) # Reemplaza espacios y otros separadores por _
    name = re.sub(r'[ÁÉÍÓÚáéíóú]', lambda m: {'Á':'a','É':'e','Í':'i','Ó':'o','Ú':'u','á':'a','é':'e','í':'i','ó':'o','ú':'u'}[m.group(0)], name)
    name = re.sub(r'[^a-zA-Z0-9_]', '', name) # Elimina caracteres no alfanuméricos restantes
    return name.lower()

def procesar_reporte_academico(input_filepath, output_filepath):
    """
    Transforma un reporte académico en formato XLSX a un formato de tabla CSV plana,
    normalizando los nombres de las columnas a snake_case.
    """
    print(f"Iniciando el procesamiento del archivo: {input_filepath}")

    try:
        df = pd.read_excel(input_filepath, header=None, engine='openpyxl')
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        return

    data_rows = []
    column_headers = None
    current_career = None

    for index, row in df.iterrows():
        first_cell = str(row.iloc[0])

        if pd.notna(row.iloc[0]) and pd.isna(row.iloc[1]):
            current_career = first_cell.strip()
            continue

        if 'Apellido y Nombre' in first_cell:
            # Normalizamos los encabezados a snake_case aquí
            raw_headers = [str(h).strip() for h in row if pd.notna(h)]
            column_headers = [to_snake_case(h) for h in raw_headers]
            column_headers.append('carrera') # Añadimos la nueva columna ya en snake_case
            print(f"-> Encabezados normalizados encontrados: {column_headers}")
            continue

        if column_headers is not None:
            if row.isnull().all():
                continue
            
            row_data = list(row)[:len(column_headers)-1]
            row_data.append(current_career)
            
            data_dict = dict(zip(column_headers, row_data))
            data_rows.append(data_dict)

    if not data_rows:
        print("Advertencia: No se encontraron datos de estudiantes para procesar.")
        return

    df_procesado = pd.DataFrame(data_rows)
    df_procesado = df_procesado[column_headers]

    try:
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        df_procesado.to_csv(output_filepath, index=False, encoding='utf-8')
        print(f"\n¡Procesamiento completado! Archivo limpio guardado en: {output_filepath}")
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo: {e}")

if __name__ == '__main__':
    #input_path = 'data/crudos/Grado_pregrado_todos.xlsx'
    #output_path = 'data/procesados/Grado_pregrado_procesado.csv'
    
    input_path = 'data/crudos/CPU_todos.xlsx'
    output_path = 'data/procesados/CPU_procesados.csv'
    
    procesar_reporte_academico(input_path, output_path)

