from dash import dcc, html, Input, Output, State, ctx, dash
import json

# Importamos la instancia de la app
from ..app import app
# Importamos las funciones para cargar datos y crear gráficos
from ..data.loader import (
    cargar_evolucion_todas,
    cargar_evolucion_grado,
    cargar_cpu_materias,
    cargar_kpis_inscripciones
)
from ..graph_factory.factory import (
    crear_grafico_estudiantes_por_carrera,
    crear_grafico_evolucion_temporal,
    crear_grafico_inscripciones_cuatrimestre,
    crear_grafico_cpu_materias,
    crear_grafico_vacio
)

# --- Carga de datos para la página ---
df_todas = cargar_evolucion_todas()
df_grado = cargar_evolucion_grado()
df_cpu_mat = cargar_cpu_materias()
kpis_insc = cargar_kpis_inscripciones()
kpi_names_insc = sorted(list(kpis_insc.keys())) if kpis_insc else []

# --- Función de ayuda para crear tarjetas KPI ---
def create_kpi_card(card_index, initial_kpi_name, initial_kpi_value):
    """Crea la estructura de una tarjeta KPI con un botón de rotación."""
    card_id = f"{card_index+1}-insc"
    return html.Div([
        html.Div([
            html.H5(initial_kpi_name, id=f'kpi-title-{card_id}'),
            html.H2(initial_kpi_value, id=f'kpi-value-{card_id}'),
            html.Button('↻', id={'type': 'kpi-change-btn', 'index': card_index}, className='kpi-change-button')
        ], className="kpi-content"),
    ], className="three columns kpi-card-container")


# --- Layout de la Página ---
initial_indices = [(i % len(kpi_names_insc)) for i in range(4)] if kpi_names_insc else [0,0,0,0]

layout = html.Div([
    html.H1("Inscripción a materias"),
    html.Div(id='kpi-row-insc', className="row", children=[
        create_kpi_card(i, 
                        kpi_names_insc[initial_indices[i]],
                        f"{kpis_insc.get(kpi_names_insc[initial_indices[i]], 0):,}".replace(',', '.'))
        for i in range(4)
    ]),
    html.Div([
        html.Div([
            html.Label("Filtrar estudiantes por:"),
            dcc.RadioItems(id='filtro-estudiantes-insc', options=[{'label': 'Todas', 'value': 'Todas'}, {'label': 'Grado', 'value': 'Grado'}], value='Todas', labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            dcc.Graph(id='grafico-estudiantes-carrera')
        ], className="six columns"),
        html.Div([
            html.Label("Filtrar evolución por:"),
            dcc.RadioItems(id='filtro-evolucion-insc', options=[{'label': 'Todas', 'value': 'Todas'}, {'label': 'Grado', 'value': 'Grado'}], value='Todas', labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            dcc.Graph(id='grafico-evolucion-temporal')
        ], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='grafico-insc-cuatri')], className="six columns"),
        html.Div([dcc.Graph(id='grafico-cpu')], className="six columns"),
    ], className="row"),
    dcc.Store(id='kpi-indices-insc', data=initial_indices)
])

# --- Callbacks ---

@app.callback(
    [Output(f'kpi-title-{i+1}-insc', 'children') for i in range(4)] +
    [Output(f'kpi-value-{i+1}-insc', 'children') for i in range(4)] +
    [Output('kpi-indices-insc', 'data')],
    [Input({'type': 'kpi-change-btn', 'index': i}, 'n_clicks') for i in range(4)],
    [State('kpi-indices-insc', 'data')],
    prevent_initial_call=True
)
def update_all_kpis(n0, n1, n2, n3, current_indices):
    if not kpi_names_insc:
        return [dash.no_update] * 9

    triggered_prop_id = ctx.triggered[0]['prop_id']
    button_id_dict = json.loads(triggered_prop_id.split('.')[0])
    card_to_change_index = button_id_dict['index']
    
    all_kpi_indices = set(range(len(kpi_names_insc)))
    used_indices = set(current_indices)
    
    if all_kpi_indices.issubset(used_indices):
        return [dash.no_update] * 9

    new_kpi_index = current_indices[card_to_change_index]
    
    while True:
        new_kpi_index = (new_kpi_index + 1) % len(kpi_names_insc)
        if new_kpi_index not in used_indices:
            break
            
    new_indices = current_indices[:]
    new_indices[card_to_change_index] = new_kpi_index
    
    new_titles = [kpi_names_insc[i] for i in new_indices]
    new_values = [f"{kpis_insc.get(kpi_names_insc[i], 0):,}".replace(',', '.') for i in new_indices]
    
    return new_titles + new_values + [new_indices]


# Callbacks de los gráficos (sin cambios)
@app.callback(Output('grafico-estudiantes-carrera', 'figure'), [Input('filtro-estudiantes-insc', 'value')])
def update_grafico_estudiantes(filtro_tipo):
    df = df_grado if filtro_tipo == 'Grado' else df_todas
    return crear_grafico_estudiantes_por_carrera(df, filtro_tipo)

@app.callback(Output('grafico-evolucion-temporal', 'figure'), [Input('filtro-evolucion-insc', 'value')])
def update_grafico_evolucion(filtro_tipo):
    df = df_grado if filtro_tipo == 'Grado' else df_todas
    return crear_grafico_evolucion_temporal(df, filtro_tipo)

@app.callback(Output('grafico-insc-cuatri', 'figure'), [Input('url', 'pathname')])
def update_grafico_insc_cuatri(pathname):
    if pathname == '/inscripciones-materias':
        return crear_grafico_inscripciones_cuatrimestre(df_todas)
    return crear_grafico_vacio()

@app.callback(Output('grafico-cpu', 'figure'), [Input('url', 'pathname')])
def update_grafico_cpu(pathname):
    if pathname == '/inscripciones-materias':
        return crear_grafico_cpu_materias(df_cpu_mat)
    return crear_grafico_vacio()

