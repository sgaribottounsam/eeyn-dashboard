from dash import dcc, html, Input, Output, State, ctx
from app import app
from data.loader import (
    cargar_datos_egresados,
    cargar_egresados_2024,
    cargar_egresados_tasa,
    cargar_kpis_egresados,
    cargar_egresados_por_anio # <-- Importamos la nueva función
)
from graph_factory.factory import (
    crear_grafico_egresados_2024,
    crear_grafico_cantidad_graduados_por_plan,
    crear_grafico_tasa_graduacion,
    crear_grafico_duracion_carrera,
    crear_grafico_egresados_por_anio # <-- Importamos la nueva función
)

# --- Carga de datos ---
df_egresados = cargar_datos_egresados()
df_egresados_2024 = cargar_egresados_2024()
df_egresados_tasa = cargar_egresados_tasa()
kpis_egr = cargar_kpis_egresados()
kpi_names_egr = sorted(list(kpis_egr.keys())) if kpis_egr else []
df_egresados_anio = cargar_egresados_por_anio() # <-- Cargamos los nuevos datos

# --- Función de ayuda ---
def create_kpi_card(card_id, initial_kpi_name, initial_kpi_value):
    """Crea la estructura de una tarjeta KPI."""
    return html.Div([
        html.Div([
            html.Button('⬅️', id=f'prev-btn-{card_id}', n_clicks=0, className='kpi-button'),
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),
        html.Div([
            html.H5(initial_kpi_name, id=f'kpi-title-{card_id}', style={'textAlign': 'center'}),
            html.H3(initial_kpi_value, id=f'kpi-value-{card_id}', style={'textAlign': 'center'}),
        ], style={'display': 'inline-block', 'width': 'calc(100% - 80px)', 'verticalAlign': 'middle'}),
        html.Div([
            html.Button('➡️', id=f'next-btn-{card_id}', n_clicks=0, className='kpi-button'),
        ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),
    ], className="six columns kpi-card")

# --- Layout ---
layout = html.Div([
    html.H1("Análisis de Egresados"),
    html.H3("Indicadores Clave y Visualizaciones"),
    html.Div([
        create_kpi_card(
            '1-egr',
            kpi_names_egr[0] if kpi_names_egr else "No disponible",
            kpis_egr.get(kpi_names_egr[0], 0) if kpi_names_egr else ""
        ),
        create_kpi_card(
            '2-egr',
            kpi_names_egr[1] if len(kpi_names_egr) > 1 else "No disponible",
            kpis_egr.get(kpi_names_egr[1], 0) if len(kpi_names_egr) > 1 else ""
        ),
    ], className="row"),
    html.Hr(),
    
    # --- Fila 1 de gráficos (CON EL NUEVO GRÁFICO) ---
    html.Div([
        # Columna 1: El nuevo gráfico de egresados por año
        html.Div([
            dcc.Graph(
                figure=crear_grafico_egresados_por_anio(df_egresados_anio)
            )
        ], className="six columns"),

        # Columna 2: Egresados por carrera en 2024
        html.Div([
            dcc.Graph(
                figure=crear_grafico_egresados_2024(df_egresados_2024)
            )
        ], className="six columns"),
    ], className="row"),

    # --- Fila 2 de gráficos ---
    html.Div([
        # Columna 1: Cantidad de graduados por plan
        html.Div([
            dcc.Graph(
                figure=crear_grafico_cantidad_graduados_por_plan(df_egresados_tasa)
            )
        ], className="six columns"),

        # Columna 2: Tasa de graduación
        html.Div([
            dcc.Graph(
                figure=crear_grafico_tasa_graduacion(df_egresados_tasa)
            )
        ], className="six columns"),
    ], className="row"),
    
    # --- Fila 3 de gráficos ---
    html.Div([
        # Columna 1: Duración de carrera
        html.Div([
            dcc.Graph(
                figure=crear_grafico_duracion_carrera(df_egresados)
            )
        ], className="six columns"),
        # Columna 2: Vacía por ahora
        html.Div([], className="six columns")
    ], className="row"),

    dcc.Store(id='kpi-index-1-egr', data=0),
    dcc.Store(id='kpi-index-2-egr', data=1)
])

# --- Callbacks ---
@app.callback(
    [Output('kpi-title-1-egr', 'children'),
     Output('kpi-value-1-egr', 'children'),
     Output('kpi-index-1-egr', 'data')],
    [Input('prev-btn-1-egr', 'n_clicks'),
     Input('next-btn-1-egr', 'n_clicks')],
    [State('kpi-index-1-egr', 'data')]
)
def update_kpi_1_egr(prev_clicks, next_clicks, current_index):
    if not kpi_names_egr: return "No disponible", "", 0
    button_id = ctx.triggered_id
    if button_id == 'prev-btn-1-egr':
        new_index = (current_index - 1) % len(kpi_names_egr)
    elif button_id == 'next-btn-1-egr':
        new_index = (current_index + 1) % len(kpi_names_egr)
    else:
        new_index = current_index
    kpi_name = kpi_names_egr[new_index]
    kpi_value = kpis_egr[kpi_name]
    return kpi_name, kpi_value, new_index

@app.callback(
    [Output('kpi-title-2-egr', 'children'),
     Output('kpi-value-2-egr', 'children'),
     Output('kpi-index-2-egr', 'data')],
    [Input('prev-btn-2-egr', 'n_clicks'),
     Input('next-btn-2-egr', 'n_clicks')],
    [State('kpi-index-2-egr', 'data')]
)
def update_kpi_2_egr(prev_clicks, next_clicks, current_index):
    if len(kpi_names_egr) < 2: return "No disponible", "", 1
    button_id = ctx.triggered_id
    if button_id == 'prev-btn-2-egr':
        new_index = (current_index - 1) % len(kpi_names_egr)
    elif button_id == 'next-btn-2-egr':
        new_index = (current_index + 1) % len(kpi_names_egr)
    else:
        new_index = current_index
    kpi_name = kpi_names_egr[new_index]
    kpi_value = kpis_egr[kpi_name]
    return kpi_name, kpi_value, new_index

