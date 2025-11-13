import dash
from dash import dcc, html, Input, Output, State, ctx, MATCH
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime

# Importamos la instancia de la app y funciones de carga y gráficos
from ..app import app
from ..data.loader import (
    cargar_inscriptos_grado_por_dia,
    cargar_inscripciones_por_anio_carrera,
    cargar_documentacion_por_dia,
    cargar_inscriptos_grado_y_pregrado_por_dia, # Add this
)
from ..graph_factory.factory import (
    crear_grafico_inscriptos_grado_por_dia,
    crear_grafico_inscripciones_por_anio_carrera,
    crear_grafico_documentacion_por_dia,
    crear_grafico_inscriptos_grado_y_pregrado_por_dia, # Add this
    COLORES_CARRERAS # <-- IMPORTAMOS EL DICCIONARIO DE COLORES
)
from ..data.loader import (
    cargar_origen_preinscripcion,
    cargar_nuevos_inscriptos_primer_ingreso,
    cargar_nuevos_inscriptos_por_carrera,
    cargar_nuevos_inscriptos_historico,
)

# --- Registro de la Página ---
dash.register_page(__name__, path='/inscripciones-carreras', name='Inscripciones a Carreras')

# --- Base de datos y helpers ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'base_de_datos', 'academica.db')

# --- Funciones para KPIs ---
def get_total_fichas_guarani():
    """Obtiene el total de personas distintas en preinscriptos para 2026."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = "SELECT COUNT(DISTINCT identificacion) FROM preinscriptos WHERE anio = '2026'"
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Total Fichas Guaraní': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_total_inscripciones_grado():
    """Obtiene el total de inscriptos a carreras de grado desde inscripciones_carreras para 2026."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT COUNT(insc.n_documento)
            FROM inscripciones_carreras insc
            JOIN propuestas prop ON insc.carrera = prop.codigo
            WHERE prop.tipo = 'Grado' AND insc.anio = '2026'
        """
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Inscripciones a Carreras de Grado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_tasa_de_procesamiento():
    """Calcula la tasa de procesamiento de preinscripciones para 2026."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query_procesadas = "SELECT COUNT(*) FROM preinscriptos WHERE estado = 'Procesada' AND anio = '2026'"
        query_listas = "SELECT COUNT(*) FROM preinscriptos WHERE estado = 'Listas para procesar' AND anio = '2026'"
        procesadas = pd.read_sql_query(query_procesadas, conn).iloc[0, 0]
        listas = pd.read_sql_query(query_listas, conn).iloc[0, 0]
        if (procesadas + listas) == 0:
            tasa = 0
        else:
            tasa = (procesadas / (procesadas + listas)) * 100
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Tasa de Procesamiento': {e}")
        tasa = "N/A"
    finally:
        conn.close()
    if isinstance(tasa, (int, float)):
        return f"{tasa:.2f}%"
    else:
        return tasa

def get_total_inscripciones_pregrado():
    """Obtiene el total de inscriptos a carreras de pregrado desde inscripciones_carreras para 2026."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT COUNT(insc.n_documento)
            FROM inscripciones_carreras insc
            JOIN propuestas prop ON insc.carrera = prop.codigo
            WHERE prop.tipo = 'Pregrado' AND insc.anio = '2026'
        """
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Inscripciones a Carreras de Pregrado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_total_inscripciones_grado_pregrado():
    """Obtiene el total de inscriptos a carreras de grado y pregrado desde inscripciones_carreras para 2026."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT COUNT(insc.n_documento)
            FROM inscripciones_carreras insc
            JOIN propuestas prop ON insc.carrera = prop.codigo
            WHERE (prop.tipo = 'Grado' OR prop.tipo = 'Pregrado') AND insc.anio = '2026'
        """
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Inscripciones Grado + Pregrado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_total_documentacion_recibida():
    """Obtiene el total de filas en la tabla docu_inscripciones."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = "SELECT COUNT(*) FROM docu_inscripciones"
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Total Documentación Recibida': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_tasa_aprobacion_documentacion():
    """Calcula la tasa de aprobación de la documentación."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Usamos un solo query para eficiencia
        query = "SELECT estado_documentacin, COUNT(*) as count FROM docu_inscripciones WHERE estado_documentacin IN ('Aprobada', 'Rechazada', 'Duplicado') GROUP BY estado_documentacin"
        df = pd.read_sql_query(query, conn)
        
        counts = df.set_index('estado_documentacin')['count'].to_dict()
        aprobadas = counts.get('Aprobada', 0)
        rechazadas = counts.get('Rechazada', 0)
        duplicados = counts.get('Duplicado', 0)

        total_evaluadas = aprobadas + rechazadas + duplicados
        
        if total_evaluadas == 0:
            tasa = 0
        else:
            tasa = (aprobadas / total_evaluadas) * 100
            
    except (IndexError, sqlite3.OperationalError) as e:
        print(f"Error al calcular KPI 'Tasa Aprobación Documentación': {e}")
        tasa = "N/A"
    finally:
        conn.close()
    
    if isinstance(tasa, (int, float)):
        return f"{tasa:.2f}%"
    else:
        return tasa

# --- Definiciones de KPIs ---
kpi_definitions = {
    "Inscripciones Grado + Pregrado": get_total_inscripciones_grado_pregrado,
    "Inscripciones a Carreras de Grado": get_total_inscripciones_grado,
    "Total Documentación Recibida": get_total_documentacion_recibida,
    "Total Fichas Guaraní": get_total_fichas_guarani,
    "Inscripciones a Carreras de Pregrado": get_total_inscripciones_pregrado,
    "Tasa Aprobación Documentación": get_tasa_aprobacion_documentacion,
    "Tasa de Procesamiento": get_tasa_de_procesamiento, 
    
}
kpi_names = list(kpi_definitions.keys())
initial_indices = list(range(4))

def create_kpi_card(card_index, initial_kpi_name, initial_kpi_value):
    """Crea la estructura de una tarjeta KPI con un botón de rotación."""
    card_id = f"{card_index+1}-carreras"
    return html.Div([
        html.Div([
            html.H5(initial_kpi_name, id=f'kpi-title-{card_id}'),
            html.H2(initial_kpi_value, id=f'kpi-value-{card_id}'),
            html.Button('↻', id={'type': 'kpi-change-btn-carreras', 'index': card_index}, className='kpi-change-button')
        ], className="kpi-content"),
    ], className="three columns kpi-card-container")

# --- Funciones para crear gráficos dinámicos ---
def grafico_distribucion_estado():
    """Crea un gráfico de barras mostrando la distribución de preinscriptos por estado."""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT estado, COUNT(*) as cantidad FROM preinscriptos GROUP BY estado ORDER BY cantidad DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    fig = px.bar(df, x='estado', y='cantidad', title='Distribución de Preinscriptos por Estado',
                 labels={'estado': 'Estado de Preinscripción', 'cantidad': 'Cantidad de Alumnos'},
                 template='plotly_white', text_auto=True)
    fig.update_traces(marker_color='#004B8D', textposition='inside')
    fig.update_layout(title_x=0.5, xaxis_tickangle=-45)
    return fig

def grafico_inscriptos_grado_2026():
    """Crea un gráfico de barras con la cantidad de inscriptos por carrera de grado en 2026."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            prop.codigo,
            prop.nombre,
            COUNT(insc.n_documento) as Cantidad
        FROM
            inscripciones_carreras insc
        JOIN
            propuestas prop ON insc.carrera = prop.codigo
        WHERE
            insc.anio = '2026' AND prop.tipo = 'Grado'
        GROUP BY
            prop.codigo, prop.nombre
        HAVING
            Cantidad > 0
        ORDER BY
            Cantidad DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    fig = px.bar(df, x='codigo', y='Cantidad', title='Inscriptos por Carrera de Grado (2026)',
                 labels={'codigo': 'Carrera', 'Cantidad': 'Cantidad de Inscriptos'},
                 template='plotly_white', 
                 text_auto=True,
                 color='codigo',
                 color_discrete_map=COLORES_CARRERAS
                )
    fig.update_traces(textposition='inside')
    fig.update_layout(title_x=0.5, xaxis_tickangle=-30, showlegend=False)
    return fig

def grafico_origen_preinscripcion(df):
    """Crea un gráfico de torta con el origen de la preinscripción."""
    if df.empty:
        return px.pie(title="Origen de la preinscripción (No hay datos)")
    
    total = df['cantidad'].sum()
    fig = px.pie(df, names='origen', values='cantidad',
                 title=f'Origen de la preinscripción (Total: {total})',
                 template='plotly_white')
    fig.update_traces(texttemplate='%{percent:.1%} (Cant: %{value})')
    fig.update_layout(title_x=0.5)
    return fig

def grafico_nuevos_inscriptos_primer_ingreso(df):
    """Crea un gráfico de barras para los nuevos inscriptos de primer ingreso."""
    if df.empty:
        return px.bar(title="Nuevos Inscriptos: Primer Ingreso (No hay datos)")
    
    fig = px.bar(df, x='primera_carrera', y='cantidad', title='Nuevos Inscriptos: Primer Ingreso',
                 labels={'primera_carrera': 'Tipo de Ingreso', 'cantidad': 'Cantidad'},
                 template='plotly_white', text_auto=True)
    fig.update_traces(marker_color='#004B8D', textposition='inside')
    fig.update_layout(title_x=0.5)
    return fig

def grafico_nuevos_inscriptos_por_carrera(df):
    """Crea un gráfico de barras para los nuevos inscriptos por carrera."""
    if df.empty:
        return px.bar(title="Nuevos Inscriptos: Por Carrera (No hay datos)")
    
    fig = px.bar(df, x='carrera', y='cantidad', title='Nuevos Inscriptos: Por Carrera',
                 labels={'carrera': 'Carrera', 'cantidad': 'Cantidad'},
                 template='plotly_white', text_auto=True,
                 color='carrera',
                 color_discrete_map=COLORES_CARRERAS)
    fig.update_traces(textposition='inside')
    fig.update_layout(title_x=0.5, showlegend=False)
    return fig

def grafico_nuevos_inscriptos_historico(df):
    """Crea un gráfico de barras agrupado y apilado para el histórico de nuevos inscriptos."""
    if df.empty:
        return px.bar(title="Nuevos Inscriptos: Histórico (No hay datos)")
    
    fig = px.bar(df, x='ano_ingreso', y='cantidad', color='carrera',
                 title='Nuevos Inscriptos: Histórico',
                 labels={'ano_ingreso': 'Año de Ingreso', 'cantidad': 'Cantidad', 'carrera': 'Carrera'},
                 template='plotly_white', text_auto=True,
                 barmode='stack',
                 color_discrete_map=COLORES_CARRERAS,
                 category_orders={'carrera': list(COLORES_CARRERAS.keys())})
    fig.update_traces(textposition='inside')
    
    # Calcular totales por año y agregar anotaciones
    df_totals = df.groupby('ano_ingreso')['cantidad'].sum().reset_index()
    for _, row in df_totals.iterrows():
        fig.add_annotation(
            x=row['ano_ingreso'],
            y=row['cantidad'],
            text=f"Total: {row['cantidad']}",
            showarrow=False,
            yshift=10
        )
        
    fig.update_layout(title_x=0.5)
    return fig

# --- Carga de Datos para gráficos no dinámicos ---
df_inscriptos_grado_dia = cargar_inscriptos_grado_por_dia()
df_insc_anio_carrera = cargar_inscripciones_por_anio_carrera()
df_docu_por_dia = cargar_documentacion_por_dia()
df_inscriptos_grado_y_pregrado_por_dia = cargar_inscriptos_grado_y_pregrado_por_dia()
df_origen_preinscripcion = cargar_origen_preinscripcion()
df_nuevos_inscriptos_primer_ingreso = cargar_nuevos_inscriptos_primer_ingreso()
df_nuevos_inscriptos_por_carrera = cargar_nuevos_inscriptos_por_carrera()
df_nuevos_inscriptos_historico = cargar_nuevos_inscriptos_historico()


# --- Filtrado para el gráfico de evolución de inscriptos ---
hoy = datetime.now()
df_filtrado = df_inscriptos_grado_dia.copy()

# Si estamos en el año 2026, filtramos los datos de ese año para que solo muestren hasta el día actual.
if hoy.year == 2026:
    dia_mes_hoy = hoy.strftime('%m-%d')
    # Excluimos las filas de 2026 cuya fecha es posterior a hoy
    condicion_a_excluir = (df_filtrado['anio'] == 2026) & (df_filtrado['dia_mes'] > dia_mes_hoy)
    df_filtrado = df_filtrado[~condicion_a_excluir]

# --- Layout de la Página ---
layout = html.Div([
    html.H1("Inscripciones a Carreras 2026"),
    html.Div(id='kpi-row-carreras', className="row", children=[
        create_kpi_card(i, kpi_names[i], kpi_definitions[kpi_names[i]]())
        for i in range(4)
    ]),
    dcc.Store(id='kpi-indices-carreras', data=initial_indices),
    html.Hr(),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'inscriptos-grado-dia'}, figure=crear_grafico_inscriptos_grado_por_dia(df_filtrado)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'inscriptos-grado-dia'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscriptos de Grado por Día")),
                dbc.ModalBody(dcc.Graph(figure=crear_grafico_inscriptos_grado_por_dia(df_filtrado), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'inscriptos-grado-dia'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'inscripciones-anio-carrera'}, figure=crear_grafico_inscripciones_por_anio_carrera(df_insc_anio_carrera)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'inscripciones-anio-carrera'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscripciones por Año y Carrera")),
                dbc.ModalBody(dcc.Graph(figure=crear_grafico_inscripciones_por_anio_carrera(df_insc_anio_carrera), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'inscripciones-anio-carrera'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'distribucion-estado'}, figure=grafico_distribucion_estado()),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'distribucion-estado'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Distribución de Preinscriptos por Estado")),
                dbc.ModalBody(dcc.Graph(figure=grafico_distribucion_estado(), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'distribucion-estado'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'inscriptos-grado-2026'}, figure=grafico_inscriptos_grado_2026()),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'inscriptos-grado-2026'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscriptos por Carrera de Grado (2026)")),
                dbc.ModalBody(dcc.Graph(figure=grafico_inscriptos_grado_2026(), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'inscriptos-grado-2026'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'documentacion-por-dia'}, figure=crear_grafico_documentacion_por_dia(df_docu_por_dia)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'documentacion-por-dia'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Documentación Recibida por Día")),
                dbc.ModalBody(dcc.Graph(figure=crear_grafico_documentacion_por_dia(df_docu_por_dia), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'documentacion-por-dia'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'inscriptos-grado-pregrado-dia'}, figure=crear_grafico_inscriptos_grado_y_pregrado_por_dia(df_inscriptos_grado_y_pregrado_por_dia)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'inscriptos-grado-pregrado-dia'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Inscriptos Grado y Pregrado por Día")),
                dbc.ModalBody(dcc.Graph(figure=crear_grafico_inscriptos_grado_y_pregrado_por_dia(df_inscriptos_grado_y_pregrado_por_dia), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'inscriptos-grado-pregrado-dia'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'nuevos-inscriptos-primer-ingreso'}, figure=grafico_nuevos_inscriptos_primer_ingreso(df_nuevos_inscriptos_primer_ingreso)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'nuevos-inscriptos-primer-ingreso'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Nuevos Inscriptos: Primer Ingreso")),
                dbc.ModalBody(dcc.Graph(figure=grafico_nuevos_inscriptos_primer_ingreso(df_nuevos_inscriptos_primer_ingreso), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'nuevos-inscriptos-primer-ingreso'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'nuevos-inscriptos-por-carrera'}, figure=grafico_nuevos_inscriptos_por_carrera(df_nuevos_inscriptos_por_carrera)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'nuevos-inscriptos-por-carrera'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Nuevos Inscriptos: Por Carrera")),
                dbc.ModalBody(dcc.Graph(figure=grafico_nuevos_inscriptos_por_carrera(df_nuevos_inscriptos_por_carrera), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'nuevos-inscriptos-por-carrera'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'origen-preinscripcion'}, figure=grafico_origen_preinscripcion(df_origen_preinscripcion)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'origen-preinscripcion'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Origen de la Preinscripción")),
                dbc.ModalBody(dcc.Graph(figure=grafico_origen_preinscripcion(df_origen_preinscripcion), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'origen-preinscripcion'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id={'type': 'graph-carreras', 'index': 'nuevos-inscriptos-historico'}, figure=grafico_nuevos_inscriptos_historico(df_nuevos_inscriptos_historico)),
            dbc.Button("Ampliar", id={'type': 'btn-modal-carreras', 'index': 'nuevos-inscriptos-historico'}, className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Nuevos Inscriptos: Histórico")),
                dbc.ModalBody(dcc.Graph(figure=grafico_nuevos_inscriptos_historico(df_nuevos_inscriptos_historico), style={'height': '80vh'}))
            ], id={'type': 'modal-carreras', 'index': 'nuevos-inscriptos-historico'}, size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
])

# --- Callbacks ---
@app.callback(
    [Output(f'kpi-title-{i+1}-carreras', 'children') for i in range(4)] +
    [Output(f'kpi-value-{i+1}-carreras', 'children') for i in range(4)] +
    [Output('kpi-indices-carreras', 'data')],
    [Input({'type': 'kpi-change-btn-carreras', 'index': i}, 'n_clicks') for i in range(4)],
    [State('kpi-indices-carreras', 'data')],
    prevent_initial_call=True
)
def update_all_kpis(n0, n1, n2, n3, current_indices):
    if not kpi_names or len(kpi_names) <= 4:
        return [dash.no_update] * 9

    triggered_prop_id = ctx.triggered[0]['prop_id']
    button_id_dict = json.loads(triggered_prop_id.split('.')[0])
    card_to_change_index = button_id_dict['index']
    
    used_indices = set(current_indices)
    
    new_kpi_index = current_indices[card_to_change_index]
    
    while True:
        new_kpi_index = (new_kpi_index + 1) % len(kpi_names)
        if new_kpi_index not in used_indices:
            break
            
    new_indices = current_indices[:]
    new_indices[card_to_change_index] = new_kpi_index
    
    new_titles = [kpi_names[i] for i in new_indices]
    new_values = [kpi_definitions[kpi_names[i]]() for i in new_indices]
    
    return new_titles + new_values + [new_indices]

@app.callback(
    Output({'type': 'modal-carreras', 'index': MATCH}, 'is_open'),
    Input({'type': 'btn-modal-carreras', 'index': MATCH}, 'n_clicks'),
    State({'type': 'modal-carreras', 'index': MATCH}, 'is_open'),
    prevent_initial_call=True
)
def toggle_modal_carreras(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open
