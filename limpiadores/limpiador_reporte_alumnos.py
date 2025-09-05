import pandas as pd
import os

def procesar_reporte_academico(input_filepath, output_filepath):
    """
    Transforma un reporte académico en formato XLSX, agrupado por carrera,
    a un formato de tabla CSV plana.

    Args:
        input_filepath (str): La ruta al archivo XLSX de entrada.
        output_filepath (str): La ruta donde se guardará el nuevo archivo CSV.
    """
    print(f"Iniciando el procesamiento del archivo: {input_filepath}")

    try:
        # Leemos el archivo XLSX sin encabezado y con el motor 'openpyxl'.
        df = pd.read_excel(input_filepath, header=None, engine='openpyxl')
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta especificada: {input_filepath}")
        return
    except ImportError:
        print("Error: La librería 'openpyxl' es necesaria para leer archivos .xlsx.")
        print("Por favor, instalala corriendo: pip install openpyxl")
        return
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        return

    data_rows = []
    column_headers = None
    current_career = None

    # Iteramos sobre cada fila del archivo
    for index, row in df.iterrows():
        first_cell = str(row.iloc[0])

        # Condición para identificar una fila de carrera
        if pd.notna(row.iloc[0]) and pd.isna(row.iloc[1]):
            current_career = first_cell.strip()
            print(f"-> Carrera encontrada: {current_career}")
            continue

        # Condición para identificar la fila de encabezados
        if 'Apellido y Nombre' in first_cell:
            column_headers = list(row)
            column_headers.append('Carrera')
            # Limpiamos los encabezados de espacios extra o valores nulos
            column_headers = [str(h).strip() for h in column_headers if pd.notna(h)]
            print(f"-> Encabezados encontrados: {column_headers}")
            continue

        # Si ya hemos encontrado los encabezados, las filas restantes son datos
        if column_headers is not None:
            if row.isnull().all():
                continue
            
            # Aseguramos que la fila tenga la misma cantidad de columnas que los encabezados (sin 'Carrera')
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
        # Asegurarnos de que el directorio de salida exista
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        df_procesado.to_csv(output_filepath, index=False, encoding='utf-8')
        print("\n¡Procesamiento completado con éxito!")
        print(f"El archivo limpio ha sido guardado en: {output_filepath}")
        print(f"Total de registros procesados: {len(df_procesado)}")
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo: {e}")


if __name__ == '__main__':
    # --- Configuración ---
    # El script asume la siguiente estructura de carpetas:
    # MI_PROYECTO/
    # ├── data/
    # │   └── Grado_pregrado_todos.xlsx
    # └── limpiadores/
    #     └── limpiador_reporte_alumnos.py (este script)

    """input_path = 'data/Grado_pregrado_todos.xlsx'
    output_path = 'data/Grado_pregrado_procesado.csv'
    """

    input_path = 'data/CPU_todos.xlsx'
    output_path = 'data/CPU_procesados.csv'
    
    # Llama a la función principal con las nuevas rutas
    procesar_reporte_academico(input_path, output_path)
