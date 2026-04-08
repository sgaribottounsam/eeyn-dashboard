from dash import dcc, html, Input, Output, State, ctx, dash, MATCH
import dash_bootstrap_components as dbc
import json

# Importamos la instancia de la app
from ..app import app
# Importamos las funciones para cargar datos y crear gráficos
from ..data.loader import (
    cargar_evolucion_todas,
    cargar_evolucion_grado,
    cargar_cpu_materias,
    cargar_kpis_inscripciones,
    cargar_estudiantes_activos
)
from ..graph_factory.factory import (
    crear_grafico_estudiantes_activos,
    crear_grafico_evolucion_temporal,
    crear_grafico_inscripciones_cuatrimestre,
    crear_grafico_cpu_materias,
    crear_grafico_vacio
)

# --- Carga de datos para la página ---
df_estudiantes_activos = cargar_estudiantes_activos()
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
    html.H1("Estudiantes Activos"),
    html.Div(id='kpi-row-insc', className="row", children=[
        create_kpi_card(i, 
                        kpi_names_insc[initial_indices[i]],
                        f"{kpis_insc.get(kpi_names_insc[initial_indices[i]], 0):,}".replace(',', '.'))
        for i in range(4)
    ]),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='grafico-estudiantes-activos', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'estudiantes-activos'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Evolución de Estudiantes Activos")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'estudiantes-activos'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'estudiantes-activos'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'estudiantes-activos'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            html.Label("Filtrar evolución por:"),
            dcc.RadioItems(id='filtro-evolucion-insc', options=[{'label': 'Todas', 'value': 'Todas'}, {'label': 'Grado', 'value': 'Grado'}], value='Todas', labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            html.Div([
                dcc.Graph(id='grafico-evolucion-temporal', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'evolucion-temporal'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Evolución Temporal")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'evolucion-temporal'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'evolucion-temporal'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'evolucion-temporal'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ], className="row"),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='grafico-insc-cuatri', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'insc-cuatri'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscripciones por Cuatrimestre")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'insc-cuatri'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'insc-cuatri'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'insc-cuatri'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            html.Div([
                dcc.Graph(id='grafico-cpu', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'cpu'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Materias CPU")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'cpu'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'cpu'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'cpu'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
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


@app.callback(
    [Output('grafico-estudiantes-activos', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'estudiantes-activos'}, 'figure')],
    [Input('url', 'pathname')]
)
def update_grafico_estudiantes_activos(pathname):
    if pathname == '/estudiantes-activos':
        figure = crear_grafico_estudiantes_activos(df_estudiantes_activos)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-evolucion-temporal', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'evolucion-temporal'}, 'figure')],
    [Input('filtro-evolucion-insc', 'value')]
)
def update_grafico_evolucion(filtro_tipo):
    df = df_grado if filtro_tipo == 'Grado' else df_todas
    figure = crear_grafico_evolucion_temporal(df, filtro_tipo)
    return figure, figure

@app.callback(
    [Output('grafico-insc-cuatri', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'insc-cuatri'}, 'figure')],
    [Input('url', 'pathname')]
)
def update_grafico_insc_cuatri(pathname):
    if pathname == '/estudiantes-activos':
        figure = crear_grafico_inscripciones_cuatrimestre(df_todas)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-cpu', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'cpu'}, 'figure')],
    [Input('url', 'pathname')]
)
def update_grafico_cpu(pathname):
    if pathname == '/estudiantes-activos':
        figure = crear_grafico_cpu_materias(df_cpu_mat)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

app.clientside_callback(
    """
    function(n1, n2, is_open) {
        const ctx = dash_clientside.callback_context;
        if (!ctx.triggered.length) return window.dash_clientside.no_update;

        const now = new Date().getTime();
        window.last_dblclick_time = window.last_dblclick_time || 0;
        const time_diff = now - window.last_dblclick_time;
        window.last_dblclick_time = now;

        if (time_diff > 0 && time_diff < 400) {
            window.last_dblclick_time = 0;
            return !is_open;
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output({'type': 'modal-materias', 'index': MATCH}, 'is_open'),
    [Input({'type': 'overlay-materias', 'index': MATCH}, 'n_clicks'),
     Input({'type': 'overlay-modal-materias', 'index': MATCH}, 'n_clicks')],
    State({'type': 'modal-materias', 'index': MATCH}, 'is_open'),
    prevent_initial_call=True
)
