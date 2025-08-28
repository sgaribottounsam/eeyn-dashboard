import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import os

# --- Configuración del script ---
# Se define la ruta relativa para buscar los archivos de datos
DATA_FOLDER = os.path.join('..', '_output')
CLEAN_INSCRIPCIONES_FILE = os.path.join(DATA_FOLDER, 'inscripciones_limpio.csv')
CARRERAS_FILE = os.path.join('..', 'data', 'carreras.xlsx')


def crear_dashboard_inscripciones():
    """
    Función principal para leer los datos, procesarlos y crear el dashboard de Dash con un filtro de visualización.
    """
    print("Iniciando la creación del dashboard...")

    # Verificar que los archivos de datos existan
    if not os.path.exists(CLEAN_INSCRIPCIONES_FILE):
        print(f"Error: No se encontró el archivo '{CLEAN_INSCRIPCIONES_FILE}'.")
        print(
            "Asegúrate de haber ejecutado el script de limpieza de datos primero y que el archivo esté en la carpeta '_output'.")
        return
    if not os.path.exists(CARRERAS_FILE):
        print(f"Error: No se encontró el archivo '{CARRERAS_FILE}'.")
        print("Asegúrate de que el archivo de carreras.xlsx exista en la carpeta padre.")
        return

    # --- Paso 1: Leer y procesar los datos con Pandas ---
    try:
        df_inscripciones = pd.read_csv(CLEAN_INSCRIPCIONES_FILE)
        df_carreras = pd.read_excel(CARRERAS_FILE)
        print("Archivos de datos cargados exitosamente.")

        # Unir los DataFrames para obtener el tipo de carrera
        # Esto es necesario para filtrar por 'Grado'
        df_inscripciones = df_inscripciones.merge(
            df_carreras[['Código', 'Tipo']],
            left_on='Carrera',
            right_on='Código',
            how='left'
        )

        # Eliminar las filas que no tienen un tipo de carrera
        df_inscripciones.dropna(subset=['Tipo'], inplace=True)

        # Agrupar los datos para la visualización de todas las carreras
        df_agrupado_todas = df_inscripciones.groupby('Carrera').size().reset_index(name='Inscritos')
        df_agrupado_todas = df_agrupado_todas.sort_values(by='Inscritos', ascending=False)

        # Filtrar los datos para la visualización de solo grado
        df_grado = df_inscripciones[df_inscripciones['Tipo'].isin(['Grado'])]
        df_agrupado_grado = df_grado.groupby('Carrera').size().reset_index(name='Inscritos')
        df_agrupado_grado = df_agrupado_grado.sort_values(by='Inscritos', ascending=False)

        print("Datos procesados y listos para la visualización.")

    except Exception as e:
        print(f"Error al leer o procesar los archivos: {e}")
        return

    # --- Paso 2: Configurar el mapa de colores para cada carrera ---
    # Colores pastel
    pastel_colors = {
        'amarillo': '#FFE366',
        'verde': '#B3E0B3',
        'rojo': '#FFB3B3',
        'violeta': '#D8BFD8',
        'azul': '#B3D6FF',
        'naranja': '#FFC999',
        'gris': '#D3D3D3'  # Color por defecto para otras carreras
    }

    # Mapa de códigos de carrera a nombres de color
    color_map_names = {
        'LI-LAGE-P': 'amarillo',  # Lic. Administración
        'CP-CCCP-PC': 'verde',  # Contador
        'LI-LECO-P': 'rojo',  # Lic. en Economía
        'LI-LEDC-P': 'violeta',  # Economía del Conocimiento
        'LI-LTUR-P': 'azul',  # Lic. en Turismo
        'CI-EEYN-P': 'naranja',  # CPU EEYN
        'CI-GUIA-P': 'naranja',  # CPU Guía de Turismo
        'CI-LTUR-P': 'naranja',  # CPU Licenciatura en Turismo
        'CI-MPCC-P': 'naranja',  # CPU Martillero Público
    }

    # Construir el mapa final con códigos de carrera y valores hexadecimales
    color_map = {codigo: pastel_colors.get(color_map_names.get(codigo), 'gris') for codigo in
                 df_inscripciones['Carrera'].unique()}

    # --- Paso 3: Configurar y ejecutar la aplicación de Dash ---
    app = Dash(__name__)

    app.layout = html.Div(
        style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'},
        children=[
            html.H1(
                "Dashboard de Inscripciones",
                style={'textAlign': 'center', 'color': '#333'}
            ),

            html.Div(
                children=[
                    html.Label("Seleccionar visualización:"),
                    dcc.RadioItems(
                        id='filtro-carreras',
                        options=[
                            {'label': 'Todas las Carreras', 'value': 'todas'},
                            {'label': 'Solo Grado', 'value': 'grado'}
                        ],
                        value='todas',  # Valor por defecto
                        inline=True,
                        style={'marginTop': '10px'}
                    ),
                ],
                style={'textAlign': 'center', 'marginBottom': '20px'}
            ),

            dcc.Graph(
                id='graph-inscripciones'
            )
        ]
    )

    # --- Paso 4: Crear el callback para la interactividad del botón ---
    @app.callback(
        Output('graph-inscripciones', 'figure'),
        Input('filtro-carreras', 'value')
    )
    def update_graph(filtro_seleccionado):
        """
        Esta función se activa cada vez que se cambia la opción del RadioItems.
        Actualiza el gráfico según el filtro seleccionado.
        """
        if filtro_seleccionado == 'todas':
            df_to_plot = df_agrupado_todas
            title = 'Cantidad de Inscripciones por Carrera (Todas)'
        else:
            df_to_plot = df_agrupado_grado
            title = 'Cantidad de Inscripciones por Carrera (Solo Grado)'

        fig = px.bar(
            df_to_plot,
            x='Carrera',
            y='Inscritos',
            title=title,
            labels={'Carrera': 'Código de Carrera', 'Inscritos': 'Número de Inscripciones'},
            color='Carrera',  # Ahora se colorea por la columna 'Carrera'
            color_discrete_map=color_map,  # Se usa el mapa de colores definido
            template='plotly_white',
            text_auto=True
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            title_font_size=24,
            font_size=12
        )
        return fig

    # Iniciar el servidor de la aplicación
    print("\n¡Dashboard listo! Ejecuta este script y accede a http://127.0.0.1:8050 en tu navegador.")
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    crear_dashboard_inscripciones()
