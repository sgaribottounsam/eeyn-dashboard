import pandas as pd
import re
import os

# --- Configuración del script ---

# Archivo con la lista de carreras válidas
CARRERAS_FILE = 'data/procesados/carreras.csv'
# Archivo crudo de inscripciones
INSCRIPCIONES_FILE = 'data/crudos/inscripciones.xlsx'
# Archivo de salida para los datos procesados
OUTPUT_FILE = 'data/procesados/inscripciones_procesado.csv'

# Define el período a agregar a los datos
PERIODO_VALUE = '2025-2'
# Define los ESTADOS a buscar. El filtro buscará si el estado CONTIENE estas palabras.
ESTADOS_UTILES = ['Aceptada', 'Pendiente', 'Rechazada']

def limpiar_y_procesar_datos():
    """
    Función principal para leer, limpiar y enriquecer los datos de inscripciones.
    Valida las carreras contra el archivo carreras.csv.
    """
    print("Iniciando el proceso de limpieza y enriquecimiento de datos...")

    if not os.path.exists(INSCRIPCIONES_FILE) or not os.path.exists(CARRERAS_FILE):
        print(f"Error: No se encontró uno de los archivos de entrada. Verifica las rutas.")
        return

    # --- Paso 1: Leer el archivo de carreras para validación ---
    try:
        df_carreras = pd.read_csv(CARRERAS_FILE, encoding='utf-8')
        codigos_carrera_validos = set(df_carreras['Codigo'])
        print(f"-> Se cargaron {len(codigos_carrera_validos)} códigos de carrera válidos.")
    except Exception as e:
        print(f"Error al leer el archivo de carreras: {e}")
        return

    # --- Paso 2: Procesar el archivo de inscripciones ---
    try:
        df_inscripciones = pd.read_excel(INSCRIPCIONES_FILE, header=None)
        
        datos_limpios = []
        current_carrera_code = None

        print("-> Procesando filas del reporte de inscripciones...")
        for index, row in df_inscripciones.iterrows():
            cell_value = str(row.iloc[0])
            match = re.search(r'\((.*?)\)', cell_value)
            
            # Condición 1: La fila es un encabezado de carrera
            if match and match.group(1) in codigos_carrera_validos:
                current_carrera_code = match.group(1)
                continue

            # Condición 2: La fila es un encabezado de columnas. La detectamos y la saltamos.
            if 'Alumno' in cell_value and 'Identificación' in str(row.iloc[1]):
                continue

            # Condición 3: La fila es un dato de alumno
            if current_carrera_code and pd.notna(row.iloc[1]):
                # CORRECCIÓN: Se ajustaron los índices de las columnas para que coincidan con el archivo Excel.
                datos_limpios.append({
                    'Alumno': row.iloc[0],
                    'Identificación': row.iloc[1],
                    'Comisión': row.iloc[3],       # Comisión está en la 4ta columna (índice 3)
                    'Estado Insc.': row.iloc[4],   # Estado Insc. está en la 5ta columna (índice 4)
                    'Fecha inscripción': row.iloc[6], # Fecha inscripción está en la 7ma columna (índice 6)
                    'Carrera': current_carrera_code,
                    'Período': PERIODO_VALUE
                })
        
        if not datos_limpios:
            print("Resultado: No se encontraron datos de inscripción válidos. Revisa el archivo de entrada.")
            return

        # --- Paso 3: Filtrar y guardar los datos limpios ---
        df_limpio = pd.DataFrame(datos_limpios)
        
        # Filtro Robusto: Busca si el estado CONTIENE alguna de las palabras clave
        filtro_regex = '|'.join(ESTADOS_UTILES)
        df_filtrado = df_limpio[df_limpio['Estado Insc.'].str.contains(filtro_regex, case=False, na=False)]
        
        print(f"\nSe encontraron {len(df_limpio)} filas de datos. Después de filtrar por estado, quedan {len(df_filtrado)} filas.")

        columnas_finales = ['Alumno', 'Identificación', 'Comisión', 'Estado Insc.', 'Fecha inscripción', 'Carrera', 'Período']
        df_final = df_filtrado[columnas_finales]

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"Proceso finalizado. Archivo limpio guardado como '{OUTPUT_FILE}'.")

    except Exception as e:
        print(f"Error al procesar el archivo de inscripciones: {e}")
        return

if __name__ == '__main__':
    limpiar_y_procesar_datos()

