
import dash
from dash import dcc, html

# Importamos la instancia de la app y funciones de carga y gráficos
from app import app
from data.loader import (
    cargar_kpis_inscripciones_carreras,
    cargar_inscriptos_por_dia,
    cargar_comparativa_inscriptos_carrera,
    cargar_preinscriptos_por_estado
)
from graph_factory.factory import (
    crear_grafico_evolucion_inscriptos_diarios,
    crear_grafico_comparativa_inscriptos_carrera,
    crear_grafico_distribucion_preinscriptos_estado
)

# --- Registro de la Página ---
dash.register_page(__name__, path='/inscripciones-carreras', name='Inscripciones a Carreras')

# --- Carga de Datos ---
df_inscriptos_dia = cargar_inscriptos_por_dia()
df_comparativa = cargar_comparativa_inscriptos_carrera()
df_estado = cargar_preinscriptos_por_estado()
kpis = cargar_kpis_inscripciones_carreras()

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
    html.H1("Inscripciones a Carreras 2025"),

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
        html.Div([dcc.Graph(figure=crear_grafico_evolucion_inscriptos_diarios(df_inscriptos_dia))], className="six columns"),
        html.Div([dcc.Graph(figure=crear_grafico_distribucion_preinscriptos_estado(df_estado))], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_comparativa_inscriptos_carrera(df_comparativa))], className="twelve columns"),
    ], className="row"),
])
