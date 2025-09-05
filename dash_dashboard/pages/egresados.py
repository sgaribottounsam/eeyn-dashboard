from dash import dcc, html

# Importamos las funciones para cargar datos y crear gráficos
from data.loader import (
    cargar_datos_egresados,
    cargar_egresados_2024,
    cargar_egresados_tasa
)
from graph_factory.factory import (
    crear_grafico_egresados_2024,
    crear_grafico_cantidad_graduados_por_plan,
    crear_grafico_tasa_graduacion,
    crear_grafico_duracion_carrera
)

# --- Carga de datos para los gráficos de esta página ---
# Como los gráficos son estáticos, cargamos los datos una sola vez al iniciar la app
df_egresados = cargar_datos_egresados()
df_egresados_2024 = cargar_egresados_2024()
df_egresados_tasa = cargar_egresados_tasa()


# --- Layout de la Página de Egresados ---
# Esta variable 'layout' será importada por index.py
layout = html.Div([
    html.H1("Análisis de Egresados"),
    html.H3("Indicadores Clave y Visualizaciones"),
    html.Hr(),

    # Fila 1 de gráficos
    html.Div([
        # Columna 1
        html.Div([
            dcc.Graph(
                figure=crear_grafico_egresados_2024(df_egresados_2024)
            )
        ], className="six columns"),

        # Columna 2
        html.Div([
            dcc.Graph(
                figure=crear_grafico_cantidad_graduados_por_plan(df_egresados_tasa)
            )
        ], className="six columns"),
    ], className="row"),

    # Fila 2 de gráficos
    html.Div([
        # Columna 1
        html.Div([
            dcc.Graph(
                figure=crear_grafico_tasa_graduacion(df_egresados_tasa)
            )
        ], className="six columns"),

        # Columna 2
        html.Div([
            dcc.Graph(
                figure=crear_grafico_duracion_carrera(df_egresados)
            )
        ], className="six columns"),
    ], className="row"),
])