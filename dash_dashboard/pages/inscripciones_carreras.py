import dash
from dash import dcc, html, Input, Output, State, ctx
import sqlite3
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime

# Importamos la instancia de la app y funciones de carga y gráficos
from app import app
from data.loader import (
    cargar_inscriptos_grado_por_dia,
    cargar_inscripciones_por_anio_carrera,
)
from graph_factory.factory import (
    crear_grafico_inscriptos_grado_por_dia,
    crear_grafico_inscripciones_por_anio_carrera,
    COLORES_CARRERAS # <-- IMPORTAMOS EL DICCIONARIO DE COLORES
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

# --- Definiciones de KPIs ---
kpi_definitions = {
    "Inscripciones Grado + Pregrado": get_total_inscripciones_grado_pregrado,
    "Inscripciones a Carreras de Grado": get_total_inscripciones_grado,
    "Total Fichas Guaraní": get_total_fichas_guarani,
    "Inscripciones a Carreras de Pregrado": get_total_inscripciones_pregrado,
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
    fig.update_traces(marker_color='#004B8D', textposition='outside')
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
    fig.update_layout(title_x=0.5, xaxis_tickangle=-30, showlegend=False)
    return fig

# --- Carga de Datos para gráficos no dinámicos ---
df_inscriptos_grado_dia = cargar_inscriptos_grado_por_dia()
df_insc_anio_carrera = cargar_inscripciones_por_anio_carrera()

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
        html.Div([dcc.Graph(figure=crear_grafico_inscriptos_grado_por_dia(df_filtrado))], className="six columns"),
        html.Div([dcc.Graph(figure=crear_grafico_inscripciones_por_anio_carrera(df_insc_anio_carrera))], className="six columns"),
    ]),
    html.Div(className="row", children=[
        html.Div([dcc.Graph(figure=grafico_distribucion_estado())], className="six columns"),
        html.Div([dcc.Graph(figure=grafico_inscriptos_grado_2026())], className="six columns"),
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