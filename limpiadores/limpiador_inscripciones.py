import pandas as pd
import re
import os

# --- Configuración del script ---
# Define el nombre de los archivos de entrada en formato XLSX
INSCRIPCIONES_FILE = 'inscripciones.xlsx'
CARRERAS_FILE = '../data/carreras.xlsx'
# Define el nombre del archivo de salida
OUTPUT_FILE = 'inscripciones_limpio.csv'
# Define el período a agregar a los datos
PERIODO_VALUE = '2025-2'
# Define los estados de inscripción que se consideran "útiles"
ESTADOS_UTILES = ['Aceptada', 'Pendiente', 'Rechazada']


def limpiar_y_procesar_datos():
    """
    Función principal para leer, limpiar y enriquecer los datos de inscripciones.
    Lee el archivo de inscripciones fila por fila, detectando los cambios de carrera
    y asignando el código de carrera correcto a cada inscripción.
    """
    print("Iniciando el proceso de limpieza y enriquecimiento de datos...")

    # Verificar que los archivos de entrada existan
    if not os.path.exists(INSCRIPCIONES_FILE):
        print(f"Error: No se encontró el archivo '{INSCRIPCIONES_FILE}'.")
        return
    if not os.path.exists(CARRERAS_FILE):
        print(f"Error: No se encontró el archivo '{CARRERAS_FILE}'.")
        return

    # --- Paso 1: Leer el archivo de carreras para validación ---
    try:
        df_carreras = pd.read_excel(CARRERAS_FILE)
        # Crear un conjunto de códigos de carrera válidos para la validación
        codigos_carreras_validos = set(df_carreras.Código.values)
        print(f"Mapeo de {len(codigos_carreras_validos)} códigos de carrera cargado exitosamente.")
    except Exception as e:
        print(f"Error al leer el archivo de carreras: {e}")
        return

    # --- Paso 2: Leer el archivo de inscripciones fila por fila para procesar ---
    datos_limpios = []
    current_carrera_code = None
    header_found = False

    try:
        # Se lee el archivo de inscripciones completo en una sola vez, sin encabezado
        df_raw = pd.read_excel(INSCRIPCIONES_FILE, header=None)

        for index, row in df_raw.iterrows():
            row_list = [str(x) for x in row.tolist()]
            row_str = ' '.join(row_list).strip()

            # Buscar la fila de encabezado que contiene 'Alumno'
            if 'Alumno' in row_str:
                header_found = True
                continue

            # Si ya se encontró el encabezado, procesar los datos
            if header_found:
                # Omitir filas completamente vacías
                if not row_str or all(pd.isna(x) for x in row):
                    continue

                # Si es una fila de datos de inscripción, procesarla
                # Se asume que las filas de datos tienen al menos 5 columnas con información
                if not pd.isna(row.iloc[0]) and any(pd.notna(x) for x in row.iloc[1:]):
                    # Usar el código de carrera actual
                    carrera_code_to_use = current_carrera_code if current_carrera_code else 'Desconocida'

                    # Crear un diccionario con los datos relevantes y los nuevos campos
                    fila_dict = {
                        'Alumno': row.iloc[0],
                        'Identificación': row.iloc[1],
                        'Comisión': row.iloc[3],
                        'Estado Insc.': row.iloc[4],
                        'Fecha inscripción': row.iloc[6],
                        'Carrera': carrera_code_to_use,
                        'Período': PERIODO_VALUE
                    }
                    datos_limpios.append(fila_dict)

            # Buscar códigos de carrera en las filas de metadatos
            # El regex busca un patrón entre paréntesis y excluye los que empiezan con MA y PF
            match = re.search(r'\(([^MPF].*?)\)', row_str)
            if match:
                new_carrera_code = match.group(1).strip()
                # Verificar si el código encontrado es válido
                if new_carrera_code in codigos_carreras_validos:
                    current_carrera_code = new_carrera_code
                    print(f"Cambiando carrera actual a: {current_carrera_code}")
                else:
                    print(f"Código de carrera no válido encontrado: {new_carrera_code}")

        if not datos_limpios:
            print("No se encontraron datos de inscripción válidos. Revisa el archivo de entrada.")
            return

        # --- Paso 3: Filtrar y guardar los datos limpios en un DataFrame ---
        df_limpio = pd.DataFrame(datos_limpios)

        # Filtrar solo por los estados de inscripción útiles
        df_filtrado = df_limpio[df_limpio['Estado Insc.'].isin(ESTADOS_UTILES)]

        print(f"Se encontraron {len(df_limpio)} filas de datos. Después de filtrar, quedan {len(df_filtrado)} filas.")

        # Seleccionar las columnas finales que nos interesan
        columnas_finales = ['Alumno', 'Identificación', 'Comisión', 'Estado Insc.', 'Fecha inscripción', 'Carrera',
                            'Período']
        df_final = df_filtrado[columnas_finales]

        # Guardar el DataFrame final en un nuevo archivo CSV
        try:
            df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
            print(f"Proceso finalizado. Archivo limpio guardado como '{OUTPUT_FILE}'.")
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")

    except Exception as e:
        print(f"Error al procesar el archivo de inscripciones: {e}")
        return


# Ejecutar la función principal
if __name__ == "__main__":
    limpiar_y_procesar_datos()
