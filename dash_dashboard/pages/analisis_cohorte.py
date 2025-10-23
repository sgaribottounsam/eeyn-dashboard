import dash
from dash import dcc, html, Input, Output, State, ctx, MATCH
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import plotly.express as px
import os
import json

# Importamos la instancia de la app
from ..app import app

# --- Registro de la Página ---
dash.register_page(__name__, path='/analisis-cohorte', name='Análisis por Cohorte')

# --- Base de datos y helpers ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'base_de_datos', 'academica.db')

def get_cohortes():
    """Obtiene los años de cohorte disponibles desde la tabla de aspirantes."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Usamos DISTINCT para obtener años únicos y filtramos desde 2006
        query = "SELECT DISTINCT ano_ingreso FROM aspirantes WHERE ano_ingreso >= 2006 ORDER BY ano_ingreso DESC"
        df = pd.read_sql_query(query, conn)
        raw_cohortes = df['ano_ingreso'].tolist()
        cohortes = []
        for c in raw_cohortes:
            if isinstance(c, bytes):
                # Los años parecen estar almacenados como bytes, los decodificamos a enteros.
                # Asumimos codificación little-endian.
                cohortes.append(int.from_bytes(c, 'little'))
            else:
                cohortes.append(c)
    except Exception as e:
        print(f"Error al obtener cohortes: {e}")
        cohortes = []
    finally:
        conn.close()
    return cohortes

# --- Funciones para KPIs ---
def get_total_aspirantes_grado(cohorte):
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"""SELECT COUNT(DISTINCT tipo_y_n_documento) 
                     FROM aspirantes 
                     WHERE ano_ingreso = {cohorte} AND 
                        (carrera LIKE '%CI-EEYN%'
                         OR carrera LIKE '%CI-LTUR%')"""
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except Exception as e:
        print(f"Error al calcular KPI 'Total Aspirantes Grado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_total_aspirantes_pregrado(cohorte):
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"""SELECT COUNT(DISTINCT tipo_y_n_documento) 
                     FROM aspirantes 
                     WHERE ano_ingreso = {cohorte} AND 
                        (carrera LIKE '%CI-MART%'
                         OR carrera LIKE '%CI-GUIA%')"""
        total = pd.read_sql_query(query, conn).iloc[0, 0]
    except Exception as e:
        print(f"Error al calcular KPI 'Total Aspirantes Pregrado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_aprobaron_cpu_grado(cohorte):
    conn = sqlite3.connect(DB_PATH)
    try:
        # Parte 1: Aspirantes que aprobaron el CPU directamente
        query_pasaron_directo = f"""SELECT DISTINCT tipo_y_n_documento 
                                     FROM aspirantes 
                                     WHERE ano_ingreso = {cohorte} 
                                       AND (carrera LIKE '%CI-EEYN%' OR carrera LIKE '%CI-LTUR%') 
                                       AND actividades_aprobadas >= total_actividades"""
        df_pasaron_directo = pd.read_sql_query(query_pasaron_directo, conn)
        pasaron_directo_set = set(df_pasaron_directo['tipo_y_n_documento'])

        # Parte 2: Aspirantes que no aprobaron pero se convirtieron en estudiantes
        query_reenganche = f"""SELECT DISTINCT a.tipo_y_n_documento
                                FROM aspirantes a
                                JOIN estudiantes e ON a.tipo_y_n_documento = e.tipo_y_n_documento
                                WHERE a.ano_ingreso = {cohorte}
                                  AND (a.carrera LIKE '%CI-EEYN%' OR a.carrera LIKE '%CI-LTUR%')
                                  AND a.actividades_aprobadas < a.total_actividades
                                  AND e.actividades_aprobadas >= 1"""
        df_reenganche = pd.read_sql_query(query_reenganche, conn)
        reenganche_set = set(df_reenganche['tipo_y_n_documento'])

        total = len(pasaron_directo_set.union(reenganche_set))

    except Exception as e:
        print(f"Error al calcular KPI 'Aprobaron CPU Grado': {e}")
        total = "N/A"
    finally:
        conn.close()
    return total

def get_tasa_aprobacion_cpu_grado(cohorte):
    total_aspirantes = get_total_aspirantes_grado(cohorte)
    aprobaron = get_aprobaron_cpu_grado(cohorte)

    # Asegurarse de que ambos valores son numéricos para el cálculo
    try:
        total_aspirantes_num = int(total_aspirantes)
        aprobaron_num = int(aprobaron)
    except (ValueError, TypeError):
        return "N/A" # Retorna N/A si los valores no son numéricos

    if total_aspirantes_num > 0:
        tasa = (aprobaron_num / total_aspirantes_num) * 100
        return f"{tasa:.2f}%"
    else:
        return "0.00%"

# --- Funciones para Gráficos ---
def create_graph_aspirantes_carrera(cohorte):
    """Crea el gráfico de aspirantes a carrera."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"""
            SELECT actividades_aprobadas
            FROM aspirantes
            WHERE ano_ingreso = {cohorte}
              AND (carrera LIKE '%CI-EEYN%' OR carrera LIKE '%CI-LTUR%')
        """
        df = pd.read_sql_query(query, conn)

        # Categorizar por materias aprobadas
        bins = [-1, 0, 1, 2, 3, float('inf')]
        labels = ['0 materias', '1 materia', '2 materias', '3 materias', '4 o más materias']
        df['categoria'] = pd.cut(df['actividades_aprobadas'], bins=bins, labels=labels)

        # Contar por categoría
        data = df['categoria'].value_counts().reset_index()
        data.columns = ['categoria', 'total']
        
        # Ordenar las categorías
        data['categoria'] = pd.Categorical(data['categoria'], categories=labels, ordered=True)
        data = data.sort_values('categoria')

        # No mostrar categorías sin estudiantes
        data = data[data['total'] > 0]

        # Asignar colores
        colors = {'0 materias': 'red', '1 materia': 'red', '2 materias': 'yellow', '3 materias': 'green', '4 o más materias': 'green'}
        
        fig = px.bar(data, 
                     x='categoria', 
                     y='total', 
                     title='Aspirantes a carrera',
                     text='total',
                     color='categoria',
                     color_discrete_map=colors)
        
        fig.update_layout(xaxis_title="Materias Aprobadas", yaxis_title="Cantidad de Aspirantes", legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5))
        
        return dcc.Graph(figure=fig)

    except Exception as e:
        print(f"Error al crear gráfico 'Aspirantes a carrera': {e}")
        return dcc.Graph(figure=px.bar(title="Error al generar gráfico"))
    finally:
        conn.close()

def create_graph_contexto_anual(cohorte):
    """Crea el gráfico de contexto anual."""
    conn = sqlite3.connect(DB_PATH)
    try:
        years_to_query = [cohorte - 2, cohorte - 1, cohorte, cohorte + 1, cohorte + 2]
        if 2025 not in years_to_query:
            years_to_query.append(2025)
        
        years_str = ",".join(map(str, years_to_query))

        query = f"""
            SELECT ano_ingreso, 
                IIF (actividades_aprobadas >= total_actividades, 'Ingresante', 'Aspirante') AS condicion_CPU,
                COUNT(*) AS total_ingresantes
            FROM aspirantes
            WHERE ano_ingreso IN ({years_str})
              AND (carrera LIKE '%CI-EEYN%' OR carrera LIKE '%CI-LTUR%')
            GROUP BY ano_ingreso, condicion_CPU
        """
        df = pd.read_sql_query(query, conn)

        fig = px.bar(df, 
                     x='ano_ingreso', 
                     y='total_ingresantes',
                     color='condicion_CPU',
                     title='Contexto anual',
                     labels={'ano_ingreso': 'Cohorte', 'total_ingresantes': 'Cantidad de Aspirantes', 'condicion_CPU': 'Condición'},
                     text='total_ingresantes',
                     barmode='stack')
        
        fig.update_layout(xaxis_title="Cohorte", yaxis_title="Cantidad de Aspirantes", legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5))
        fig.update_xaxes(type='category')
        fig.update_traces(textposition='inside')

        return dcc.Graph(figure=fig)

    except Exception as e:
        print(f"Error al crear gráfico 'Contexto anual': {e}")
        return dcc.Graph(figure=px.bar(title="Error al generar gráfico"))
    finally:
        conn.close()

def create_graph_estudiantes_grado(cohorte):
    """Crea el gráfico de estudiantes de grado."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"""
            SELECT e.carrera, COUNT(DISTINCT e.tipo_y_n_documento) AS total_ingresantes
            FROM estudiantes e
            INNER JOIN aspirantes a ON e.tipo_y_n_documento = a.tipo_y_n_documento
            
            WHERE a.ano_ingreso = {cohorte}
              AND (a.actividades_aprobadas >= a.total_actividades OR e.actividades_aprobadas >= 1)
              AND (e.carrera LIKE '%LI-%' OR e.carrera LIKE '%CP-%')
            GROUP BY e.carrera; 
        """
        df = pd.read_sql_query(query, conn)

        # Extraer el código de la carrera de entre paréntesis, con fallback al nombre original
        df['carrera_code'] = df['carrera'].str.extract(r'\((.*?)\)').fillna(df['carrera'])

        fig = px.bar(df, 
                     x='carrera_code', 
                     y='total_ingresantes', 
                     title='Estudiantes de grado',
                     text='total_ingresantes')
        
        fig.update_layout(xaxis_title="Carrera", yaxis_title="Cantidad de Estudiantes")

        return dcc.Graph(figure=fig)

    except Exception as e:
        print(f"Error al crear gráfico 'Estudiantes de grado': {e}")
        return dcc.Graph(figure=px.bar(title="Error al generar gráfico"))
    finally:
        conn.close()

def create_graph_porcentaje_avance(cohorte):
    """Crea el gráfico de porcentaje de avance."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = f"""
            SELECT 
                e.carrera, 
                CASE
                    WHEN e.actividades_aprobadas = 0 THEN 'Sin avance'
                    WHEN CAST(e.actividades_aprobadas AS REAL) / e.total_actividades < 0.25 THEN 'hasta 25% avance'
                    WHEN CAST(e.actividades_aprobadas AS REAL) / e.total_actividades < 0.5 THEN '25% a 50% avance'
                    WHEN CAST(e.actividades_aprobadas AS REAL) / e.total_actividades < 0.75 THEN '50% a 75% avance'
                    WHEN CAST(e.actividades_aprobadas AS REAL) / e.total_actividades < 0.98 THEN '75% a 99% avance'
                    WHEN CAST(e.actividades_aprobadas AS REAL) / e.total_actividades < 1.1 THEN '100% avance'
                    ELSE 'REVISAR AVANCE'
                END AS avance,
                COUNT(DISTINCT e.tipo_y_n_documento) AS total_estudiantes
            FROM estudiantes AS e
            LEFT JOIN aspirantes AS a ON e.tipo_y_n_documento = a.tipo_y_n_documento
            WHERE e.tipo_y_n_documento IN (
                SELECT tipo_y_n_documento FROM aspirantes WHERE ano_ingreso = {cohorte}
            ) AND (e.carrera LIKE '%LI-%' OR e.carrera LIKE '%CP-%')
            AND (a.actividades_aprobadas >= a.total_actividades OR e.actividades_aprobadas >= 1)
            GROUP BY e.carrera, avance
        """
        df = pd.read_sql_query(query, conn)

        # Extraer el código de la carrera de entre paréntesis, con fallback al nombre original
        df['carrera_code'] = df['carrera'].str.extract(r'\((.*?)\)').fillna(df['carrera'])

        # Ordenar el eje x de forma personalizada
        category_order = [
            'Sin avance',
            'hasta 25% avance',
            '25% a 50% avance',
            '50% a 75% avance',
            '75% a 99% avance',
            '100% avance',
            'REVISAR AVANCE'
        ]
        df['avance'] = pd.Categorical(df['avance'], categories=category_order, ordered=True)
        df = df.sort_values('avance')

        fig = px.bar(df, 
                     x='avance', 
                     y='total_estudiantes', 
                     color='carrera_code',
                     title='Porcentaje de avance por carrera',
                     barmode='stack')
        
        fig.update_layout(xaxis_title="Porcentaje de Avance", yaxis_title="Cantidad de Estudiantes", legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5))
        fig.update_yaxes(showgrid=True)

        return dcc.Graph(figure=fig)

    except Exception as e:
        print(f"Error al crear gráfico 'Porcentaje de avance': {e}")
        return dcc.Graph(figure=px.bar(title="Error al generar gráfico"))
    finally:
        conn.close()

# --- Layout de la Página ---
def create_kpi_card(title, value, card_id):
    """Crea la estructura de una tarjeta KPI."""
    return html.Div([
        html.Div([
            html.H5(title, id=f'kpi-title-{card_id}'),
            html.H2(value, id=f'kpi-value-{card_id}'),
        ], className="kpi-content"),
    ], className="three columns kpi-card-container")

layout = html.Div([
    html.H1("Análisis por Cohorte"),
    
    # Selector de Cohorte
    html.Div([
        html.Label("Seleccionar Cohorte (Año de Ingreso):"),
        dcc.Dropdown(
            id='dropdown-cohorte',
            options=[{'label': str(anio), 'value': anio} for anio in get_cohortes()],
            value=get_cohortes()[0] if get_cohortes() else None, # Selecciona el último año por defecto
            clearable=False
        ),
    ], className="row", style={'marginBottom': '20px'}),

    # Fila de KPIs
    html.Div(id='kpi-row-cohorte', className="row"),

    html.Hr(),

    # Fila de Gráficos
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id='graph-cohorte-1'),
            dbc.Button("Ampliar", id='btn-modal-cohorte-1', className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Aspirantes a carrera")),
                dbc.ModalBody(dcc.Graph(id='modal-graph-1', style={'height': '80vh'}))
            ], id='modal-cohorte-1', size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id='graph-cohorte-2'),
            dbc.Button("Ampliar", id='btn-modal-cohorte-2', className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Contexto anual")),
                dbc.ModalBody(dcc.Graph(id='modal-graph-2', style={'height': '80vh'}))
            ], id='modal-cohorte-2', size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
    html.Div(className="row", children=[
        html.Div([
            dcc.Graph(id='graph-cohorte-3'),
            dbc.Button("Ampliar", id='btn-modal-cohorte-3', className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Estudiantes de grado")),
                dbc.ModalBody(dcc.Graph(id='modal-graph-3', style={'height': '80vh'}))
            ], id='modal-cohorte-3', size="xl", is_open=False)
        ], className="six columns position-relative"),
        html.Div([
            dcc.Graph(id='graph-cohorte-4'),
            dbc.Button("Ampliar", id='btn-modal-cohorte-4', className="btn-sm float-end"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Porcentaje de avance")),
                dbc.ModalBody(dcc.Graph(id='modal-graph-4', style={'height': '80vh'}))
            ], id='modal-cohorte-4', size="xl", is_open=False)
        ], className="six columns position-relative"),
    ]),
])

# --- Callbacks ---
@app.callback(
    [Output('kpi-row-cohorte', 'children'),
     Output('graph-cohorte-1', 'figure'),
     Output('graph-cohorte-2', 'figure'),
     Output('graph-cohorte-3', 'figure'),
     Output('graph-cohorte-4', 'figure'),
     Output('modal-graph-1', 'figure'),
     Output('modal-graph-2', 'figure'),
     Output('modal-graph-3', 'figure'),
     Output('modal-graph-4', 'figure')],
    [Input('dropdown-cohorte', 'value')]
)
def update_page_cohorte(selected_cohorte):
    if not selected_cohorte:
        empty_fig = px.bar()
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # --- Definiciones de KPIs ---
    kpi_definitions = {
        "Total Aspirantes Grado": get_total_aspirantes_grado,
        "Total Aspirantes Pregrado": get_total_aspirantes_pregrado,
        "Aprobaron CPU (Grado)": get_aprobaron_cpu_grado,
        "Tasa Aprobación CPU (Grado)": get_tasa_aprobacion_cpu_grado,
    }

    kpi_cards = [create_kpi_card(name, func(selected_cohorte), f"{i+1}-cohorte") 
                 for i, (name, func) in enumerate(kpi_definitions.items())]

    # --- Gráficos ---
    graph_1 = create_graph_aspirantes_carrera(selected_cohorte)
    graph_2 = create_graph_contexto_anual(selected_cohorte)
    graph_3 = create_graph_estudiantes_grado(selected_cohorte)
    graph_4 = create_graph_porcentaje_avance(selected_cohorte)
    
    fig1 = graph_1.figure
    fig2 = graph_2.figure
    fig3 = graph_3.figure
    fig4 = graph_4.figure

    return kpi_cards, fig1, fig2, fig3, fig4, fig1, fig2, fig3, fig4


for i in range(1, 5):
    @app.callback(
        Output(f'modal-cohorte-{i}', 'is_open'),
        Input(f'btn-modal-cohorte-{i}', 'n_clicks'),
        State(f'modal-cohorte-{i}', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_modal_cohorte(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open