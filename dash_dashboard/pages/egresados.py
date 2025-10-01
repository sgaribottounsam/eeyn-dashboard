from dash import dcc, html, Input, Output, State, ctx, dash
import json

# Importamos la instancia de la app
from ..app import app
# Importamos las funciones para cargar datos y crear gráficos
from ..data.loader import (
    cargar_datos_egresados,
    cargar_egresados_tasa,
    cargar_kpis_egresados,
    cargar_evolucion_egresados
)
from ..graph_factory.factory import (
    crear_grafico_cantidad_graduados_por_plan,
    crear_grafico_tasa_graduacion,
    crear_grafico_duracion_carrera,
    crear_grafico_evolucion_egresados
)

# --- Carga de datos para la página ---
df_egresados = cargar_datos_egresados()
df_egresados_tasa = cargar_egresados_tasa()
kpis_egr = cargar_kpis_egresados()
kpi_names_egr = sorted(list(kpis_egr.keys())) if kpis_egr else []
df_evolucion_egresados = cargar_evolucion_egresados()

# --- Función de ayuda para crear tarjetas KPI ---
def create_kpi_card(card_index, initial_kpi_name, initial_kpi_value):
    """Crea la estructura de una tarjeta KPI con un botón de rotación."""
    card_id = f"{card_index+1}-egr" # ID único para la página de egresados
    return html.Div([
        html.Div([
            html.H5(initial_kpi_name, id=f'kpi-title-{card_id}'),
            html.H2(initial_kpi_value, id=f'kpi-value-{card_id}'),
            html.Button('↻', id={'type': 'kpi-change-btn-egr', 'index': card_index}, className='kpi-change-button')
        ], className="kpi-content"),
    ], className="three columns kpi-card-container")


# --- Layout de la Página ---
initial_indices = [(i % len(kpi_names_egr)) for i in range(4)] if kpi_names_egr else [0,0,0,0]

layout = html.Div([
    html.H1("Egresados"),

    # Fila de KPIs con 4 tarjetas
    html.Div(id='kpi-row-egr', className="row", children=[
        create_kpi_card(i, 
                        kpi_names_egr[initial_indices[i]],
                        kpis_egr.get(kpi_names_egr[initial_indices[i]], 0))
        for i in range(4)
    ]),
    
    html.Hr(),

    # Filas de gráficos
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_evolucion_egresados(df_evolucion_egresados))], className="six columns"),
        html.Div([dcc.Graph(figure=crear_grafico_cantidad_graduados_por_plan(df_egresados_tasa))], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_tasa_graduacion(df_egresados_tasa))], className="six columns"),
        html.Div([dcc.Graph(figure=crear_grafico_duracion_carrera(df_egresados))], className="six columns"),
    ], className="row"),

    # Almacenamiento invisible para los índices de todos los KPIs
    dcc.Store(id='kpi-indices-egr', data=initial_indices)
])

# --- Callbacks ---

@app.callback(
    [Output(f'kpi-title-{i+1}-egr', 'children') for i in range(4)] +
    [Output(f'kpi-value-{i+1}-egr', 'children') for i in range(4)] +
    [Output('kpi-indices-egr', 'data')],
    [Input({'type': 'kpi-change-btn-egr', 'index': i}, 'n_clicks') for i in range(4)],
    [State('kpi-indices-egr', 'data')],
    prevent_initial_call=True
)
def update_all_kpis_egr(n0, n1, n2, n3, current_indices):
    if not kpi_names_egr:
        return [dash.no_update] * 9

    triggered_prop_id = ctx.triggered[0]['prop_id']
    button_id_dict = json.loads(triggered_prop_id.split('.')[0])
    card_to_change_index = button_id_dict['index']
    
    all_kpi_indices = set(range(len(kpi_names_egr)))
    used_indices = set(current_indices)
    
    if all_kpi_indices.issubset(used_indices):
        return [dash.no_update] * 9

    new_kpi_index = current_indices[card_to_change_index]
    
    while True:
        new_kpi_index = (new_kpi_index + 1) % len(kpi_names_egr)
        if new_kpi_index not in used_indices:
            break
            
    new_indices = current_indices[:]
    new_indices[card_to_change_index] = new_kpi_index
    
    new_titles = [kpi_names_egr[i] for i in new_indices]
    new_values = [kpis_egr.get(kpi, 0) for kpi in new_titles]
    
    return new_titles + new_values + [new_indices]

