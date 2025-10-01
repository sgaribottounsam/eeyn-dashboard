import dash
from dash import dcc, html
import sqlite3
import pandas as pd
import plotly.express as px
import os

# Importamos la instancia de la app y funciones de carga y gráficos
from app import app
from data.loader import (
    cargar_kpis_inscripciones_carreras,
    cargar_inscriptos_grado_por_dia,
    cargar_inscripciones_por_anio_carrera, # Nueva función
    # Se elimina cargar_preinscriptos_por_estado
)
from graph_factory.factory import (
    crear_grafico_inscriptos_grado_por_dia,
    crear_grafico_inscripciones_por_anio_carrera, # Nueva función
    # Se elimina crear_grafico_distribucion_preinscriptos_estado
)

# --- Registro de la Página ---
dash.register_page(__name__, path='/inscripciones-carreras', name='Inscripciones a Carreras')

# --- Carga de Datos (KPIs y otros gráficos) ---
df_inscriptos_grado_dia = cargar_inscriptos_grado_por_dia()
df_insc_anio_carrera = cargar_inscripciones_por_anio_carrera() # Nuevos datos
kpis = cargar_kpis_inscripciones_carreras()

# --- Nueva función para el gráfico de distribución por estado ---
def grafico_distribucion_estado():
    """
    Crea un gráfico de barras mostrando la distribución de preinscriptos por estado,
    leyendo los datos directamente desde la base de datos.
    """
    # --- Conexión a la Base de Datos ---
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'base_de_datos', 'academica.db')
    conn = sqlite3.connect(db_path)

    # --- Consulta SQL ---
    query = "SELECT estado, COUNT(*) as cantidad FROM preinscriptos GROUP BY estado ORDER BY cantidad DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # --- Creación del Gráfico ---
    fig = px.bar(
        df,
        x='estado',
        y='cantidad',
        title='Distribución de Preinscriptos por Estado',
        labels={'estado': 'Estado de Preinscripción', 'cantidad': 'Cantidad de Alumnos'},
        template='plotly_white',
        text_auto=True
    )
    fig.update_traces(marker_color='#004B8D', textposition='outside')
    fig.update_layout(
        title_x=0.5,
        xaxis_tickangle=-45
    )
    return fig

# --- Función de ayuda para crear tarjetas KPI estáticas ---
def create_static_kpi_card(title, value):
    """Crea una tarjeta KPI estática.""" 
    return html.Div([
        html.Div([
            html.H5(title),
            html.H2(value),
        ], className="kpi-content"),
    ], className="three columns kpi-card-container")

# --- Layout de la Página ---
layout = html.Div([
    html.H1("Inscripciones a Carreras 2026"), # <-- AÑO ACTUALIZADO

    # Fila de KPIs
    html.Div(className="row", children=[
        create_static_kpi_card("Total Preinscriptos", kpis.get('Total Preinscriptos', 'N/A')),
        create_static_kpi_card("Total Inscriptos Aceptados", kpis.get('Total Inscriptos Aceptados', 'N/A')),
        create_static_kpi_card("Tasa de Conversión (%)", f"{kpis.get('Tasa de Conversión (%)', 'N/A')}%"),
        create_static_kpi_card("Principal Estado Preinscripción", kpis.get('Principal Estado Preinscripción', 'N/A')),
    ]),
    
    html.Hr(),

    # Filas de gráficos
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_inscriptos_grado_por_dia(df_inscriptos_grado_dia))], className="six columns"),
        html.Div([dcc.Graph(figure=crear_grafico_inscripciones_por_anio_carrera(df_insc_anio_carrera))], className="six columns"),
    ], className="row"),
    html.Div([
        # Gráfico de distribución por estado AHORA es dinámico
        html.Div([dcc.Graph(figure=grafico_distribucion_estado())], className="twelve columns"),
    ], className="row"),
])
