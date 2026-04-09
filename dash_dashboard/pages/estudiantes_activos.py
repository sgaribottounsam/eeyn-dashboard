from dash import dcc, html, Input, Output, State, ctx, dash, MATCH
import dash_bootstrap_components as dbc
import json
import pandas as pd

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
    crear_grafico_evolucion_temporal_dinamico,
    crear_grafico_inscripciones_cuatrimestre,
    crear_grafico_inscripciones_cuatrimestre_dinamico,
    crear_grafico_cpu_materias,
    crear_grafico_vacio
)
from ..graph_factory.builders import build_pie_chart
from ..graph_factory.theme import COLORES_CARRERAS

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
    html.H1("Inscripciones a Cursadas"),
    html.Div(id='kpi-row-insc', className="row", children=[
        create_kpi_card(i, 
                        kpi_names_insc[initial_indices[i]],
                        f"{kpis_insc.get(kpi_names_insc[initial_indices[i]], 0):,}".replace(',', '.'))
        for i in range(4)
    ]),
    html.Div([
        html.Div([
            html.Label("Filtrar por Cuatrimestre:"),
            dcc.RadioItems(id='filtro-cuatrimestre-activos', 
                           options=[{'label': '1', 'value': '1'}, 
                                    {'label': '2', 'value': '2'}, 
                                    {'label': 'Verano', 'value': '3'}, 
                                    {'label': 'Anual', 'value': 'Anual'}], 
                           value='Anual', 
                           labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
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
            html.Br(),
            html.Label("Filtrar por Cuatrimestre:"),
            dcc.RadioItems(id='filtro-cuatrimestre-evolucion', 
                           options=[{'label': '1', 'value': '1'}, 
                                    {'label': '2', 'value': '2'}, 
                                    {'label': 'Verano', 'value': '3'}, 
                                    {'label': 'Anual', 'value': 'Anual'}], 
                           value='Anual', 
                           labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
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
            html.Label("Filtrar por Cuatrimestre:"),
            dcc.RadioItems(id='filtro-cuatrimestre-insc', 
                           options=[{'label': '1', 'value': '1'}, 
                                    {'label': '2', 'value': '2'}, 
                                    {'label': 'Verano', 'value': '3'}, 
                                    {'label': 'Anual', 'value': 'Anual'}], 
                           value='Anual', 
                           labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
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
            html.Label("Filtrar por Cuatrimestre:"),
            dcc.RadioItems(id='filtro-cuatrimestre-insc-cpu', 
                           options=[{'label': '1', 'value': '1'}, 
                                    {'label': '2', 'value': '2'}, 
                                    {'label': 'Anual', 'value': 'Anual'}], 
                           value='Anual', 
                           labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            html.Div([
                dcc.Graph(id='grafico-insc-cpu', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'insc-cpu'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscripciones a cursadas del CPU")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'insc-cpu'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'insc-cpu'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'insc-cpu'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ], className="row"),
    html.Div([
        html.Div([
            html.H3(" ", style={'opacity': 0}), # Spacer para alinear
            html.Div([
                dcc.Graph(id='grafico-comp-2026', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'comp-2026'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Composición de la Población 2026")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'comp-2026'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'comp-2026'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'comp-2026'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        
        html.Div([
            html.H3(id='total-comp-propuestas', style={'textAlign': 'center', 'color': '#8200e1', 'marginBottom': '0px'}),
            html.Div([
                dcc.Graph(id='grafico-comp-propuestas-2026', config={'displayModeBar': False}),
                html.Div(id={'type': 'overlay-materias', 'index': 'comp-prop-2026'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para ampliar")
            ], style={'position': 'relative'}),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Composición por Propuestas")),
                dbc.ModalBody(html.Div([
                    dcc.Graph(id={'type': 'modal-graph-materias', 'index': 'comp-prop-2026'}, style={'height': '80vh'}, config={'displayModeBar': False}),
                    html.Div(id={'type': 'overlay-modal-materias', 'index': 'comp-prop-2026'}, style={'position': 'absolute', 'top': '0', 'left': '0', 'width': '100%', 'height': '40px', 'zIndex': '10', 'cursor': 'pointer'}, title="Doble click para achicar")
                ], style={'position': 'relative', 'width': '100%', 'height': '100%'}))
            ], id={'type': 'modal-materias', 'index': 'comp-prop-2026'}, size="xl", is_open=False)
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
    [Input('url', 'pathname'),
     Input('filtro-cuatrimestre-activos', 'value')]
)
def update_grafico_estudiantes_activos(pathname, cuatrimestre):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio()
            
        df = df_estudiantes_activos.copy()
        if cuatrimestre != 'Anual':
            df = df[df['cuatrimestre'] == cuatrimestre]
            
        df_group = df.groupby(['anio', 'tipo'])['identificacion'].nunique().reset_index()
        df_group.rename(columns={'identificacion': 'total_estudiantes'}, inplace=True)
        
        # Ensure correct order of types
        orden_tipos = ['Curso de Ingreso', 'Pregrado', 'Grado', 'Posgrado']
        df_group['tipo'] = pd.Categorical(df_group['tipo'], categories=orden_tipos, ordered=True)
        df_group = df_group.sort_values(['anio', 'tipo'])

        figure = crear_grafico_estudiantes_activos(df_group)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-evolucion-temporal', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'evolucion-temporal'}, 'figure')],
    [Input('url', 'pathname'),
     Input('filtro-evolucion-insc', 'value'),
     Input('filtro-cuatrimestre-evolucion', 'value')]
)
def update_grafico_evolucion(pathname, filtro_tipo, cuatrimestre):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio()
            
        df = df_estudiantes_activos.copy()
        if filtro_tipo == 'Grado':
            df = df[df['tipo'] == 'Grado']
            
        if cuatrimestre != 'Anual':
            df = df[df['cuatrimestre'] == cuatrimestre]
            
        df_group = df.groupby(['anio', 'carrera'])['identificacion'].nunique().reset_index()
        df_group.rename(columns={'anio': 'año', 'identificacion': 'estudiantes'}, inplace=True)
        
        figure = crear_grafico_evolucion_temporal_dinamico(df_group, filtro_tipo)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-insc-cuatri', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'insc-cuatri'}, 'figure')],
    [Input('url', 'pathname'),
     Input('filtro-cuatrimestre-insc', 'value')]
)
def update_grafico_insc_cuatri(pathname, cuatrimestre):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio()
            
        df = df_estudiantes_activos.copy()
        
        # Filtramos a carreras de Grado únicamente
        df = df[df['tipo'] == 'Grado']
        
        # Filtramos cuatrimestre
        if cuatrimestre != 'Anual':
            df = df[df['cuatrimestre'] == cuatrimestre]
            
        # Agrupamos por año y carrera contando inscripciones (size)
        df_group = df.groupby(['anio', 'carrera']).size().reset_index()
        df_group.rename(columns={'anio': 'año', 0: 'estudiantes'}, inplace=True)
        
        figure = crear_grafico_inscripciones_cuatrimestre_dinamico(df_group, cuatrimestre)
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-insc-cpu', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'insc-cpu'}, 'figure')],
    [Input('url', 'pathname'),
     Input('filtro-cuatrimestre-insc-cpu', 'value')]
)
def update_grafico_insc_cpu(pathname, cuatrimestre):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio()
            
        df = df_estudiantes_activos.copy()
        
        # Filtramos a cursos de ingreso únicamente
        df = df[df['tipo'] == 'Curso de Ingreso']
        
        # Filtramos cuatrimestre
        if cuatrimestre != 'Anual':
            df = df[df['cuatrimestre'] == cuatrimestre]
            
        # Agrupamos por año y carrera contando inscripciones (size)
        df_group = df.groupby(['anio', 'carrera']).size().reset_index()
        df_group.rename(columns={'anio': 'año', 0: 'estudiantes'}, inplace=True)
        
        figure = crear_grafico_inscripciones_cuatrimestre_dinamico(df_group, cuatrimestre, titulo="Inscripciones a cursadas del CPU")
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-comp-2026', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'comp-2026'}, 'figure')],
    [Input('url', 'pathname')]
)
def update_grafico_comp_2026(pathname):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio()
        
        df_2026 = df_estudiantes_activos[df_estudiantes_activos['anio'] == '2026']
        df_group = df_2026.groupby('tipo').size().reset_index(name='inscripciones')
        
        figure = build_pie_chart(df_group, names='tipo', values='inscripciones', title='Composición de Inscripciones 2026')
        return figure, figure
    return crear_grafico_vacio(), crear_grafico_vacio()

@app.callback(
    [Output('grafico-comp-propuestas-2026', 'figure'),
     Output({'type': 'modal-graph-materias', 'index': 'comp-prop-2026'}, 'figure'),
     Output('total-comp-propuestas', 'children')],
    [Input('url', 'pathname'),
     Input('grafico-comp-2026', 'clickData')]
)
def update_grafico_comp_propuestas(pathname, clickData):
    if pathname == '/estudiantes-activos':
        if df_estudiantes_activos.empty:
            return crear_grafico_vacio(), crear_grafico_vacio(), ""
        
        tipo_seleccionado = 'Grado'
        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            tipo_seleccionado = clickData['points'][0]['label']
            
        df_2026 = df_estudiantes_activos[(df_estudiantes_activos['anio'] == '2026') & (df_estudiantes_activos['tipo'] == tipo_seleccionado)]
        
        total = len(df_2026)
        total_text = f"Total {tipo_seleccionado}: {total:,}".replace(',', '.')
        
        df_group = df_2026.groupby('carrera').size().reset_index(name='inscripciones')
        
        figure = build_pie_chart(df_group, names='carrera', values='inscripciones', title=f'Propuestas en {tipo_seleccionado} (2026)', color_map=COLORES_CARRERAS)
        
        return figure, figure, total_text
    return crear_grafico_vacio(), crear_grafico_vacio(), ""

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
