import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    'CP': '#5dae8b',
    'LAGE': '#f6f49d',
    'LECO': '#ff7676',
    'LEDC': '#FF8C00',
    'LTUR': '#466c95',
    'MPCC': '#c5705d',
    'GUIA': '#8B4513',
    'CPU': '#8200e1'
}

COLORES_PLANES = {
    'Plan nuevo': '#5dae8b',
    'Plan Viejo': '#466c95'
}

# --- Inicialización de la App Dash ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# --- Carga de Datos ---
def cargar_evolucion_todas():
    try:
        df = pd.read_csv('_output/inscripciones_materias/TODAS_evolucion.csv', encoding='utf-8')
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)
        df = df.dropna(how='all')
        return df[~df['Inscripciones'].str.contains('Total', na=False)]
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo TODAS_evolucion.csv")
        return pd.DataFrame()

def cargar_evolucion_grado():
    try:
        df = pd.read_csv('_output/inscripciones_materias/GRADO_evolucion.csv', encoding='utf-8')
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)
        df = df.dropna(how='all')
        return df[~df['Inscripciones'].str.contains('Total', na=False)]
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo GRADO_evolucion.csv")
        return pd.DataFrame()

def cargar_cpu_materias():
    try:
        return pd.read_csv('_output/inscripciones_materias/CPU_cantidad_materias.csv', decimal=',', encoding='utf-8')
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo CPU_cantidad_materias.csv")
        return pd.DataFrame()

def cargar_datos_egresados():
    try:
        df = pd.read_csv('_output/egresados/Egresados_duración.csv', encoding='utf-8', decimal=',')
        df.columns = ['Carrera - Plan', 'Cantidad desde 1994', 'Duración promedio', 'Cantidad (Inscriptos 2009 en adelante)', 'Duración (2009 en adelante)']
        return df
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo Egresados_duración.csv")
        return pd.DataFrame()

def cargar_egresados_2024():
    try:
        df = pd.read_csv('_output/egresados/Egresados_2024.csv', encoding='utf-8', decimal=',')
        df.columns = ['Carrera', 'Cantidad', 'Duración Promedio']
        return df[df['Carrera'] != 'Total']
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo Egresados_2024.csv")
        return pd.DataFrame()

def cargar_egresados_tasa():
    try:
        df = pd.read_csv('_output/egresados/Egresados_tasa.csv', encoding='utf-8', decimal=',')
        df['Tasa'] = df['Tasa'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        return df
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo Egresados_tasa.csv")
        return pd.DataFrame()

# Carga global de los dataframes
df_todas = cargar_evolucion_todas()
df_grado = cargar_evolucion_grado()
df_cpu_mat = cargar_cpu_materias()
df_egresados = cargar_datos_egresados()
df_egresados_2024 = cargar_egresados_2024()
df_egresados_tasa = cargar_egresados_tasa()

# --- Funciones de Gráficos ---
def crear_grafico_vacio(titulo="Datos no disponibles"):
    fig = px.bar()
    fig.update_layout(
        title=titulo,
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            'text': 'No se pudieron cargar los datos para este gráfico.',
            'xref': 'paper',
            'yref': 'paper',
            'showarrow': False,
            'font': {'size': 14}
        }],
        plot_bgcolor='white'
    )
    return fig

def crear_grafico_estudiantes_por_carrera(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return crear_grafico_vacio(f"Estudiantes por Carrera 2025 ({filtro_tipo})")
    carreras_2025 = df_evolucion[['Inscripciones', '2025']].copy()
    carreras_2025.columns = ['Carrera', 'Estudiantes']
    carreras_2025 = carreras_2025.sort_values('Estudiantes', ascending=True)
    df_filtered = carreras_2025[carreras_2025['Carrera'].isin(COLORES_CARRERAS.keys())]
    fig = px.bar(df_filtered, y='Carrera', x='Estudiantes', orientation='h', color='Carrera',
                 color_discrete_map=COLORES_CARRERAS, text='Estudiantes', title=f"👥 Estudiantes por Carrera 2025 ({filtro_tipo})")
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Cantidad de Estudiantes", yaxis_title="Carrera", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_evolucion_temporal(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return crear_grafico_vacio(f"Evolución Temporal ({filtro_tipo})")
    df_melted = df_evolucion.melt(id_vars=['Inscripciones'], value_vars=['2020', '2021', '2022', '2023', '2024', '2025'], var_name='Año', value_name='Estudiantes')
    df_melted.columns = ['Carrera', 'Año', 'Estudiantes']
    fig = px.line(df_melted, x='Año', y='Estudiantes', color='Carrera', color_discrete_map=COLORES_CARRERAS, markers=True, title=f"📈 Evolución Temporal por Carrera ({filtro_tipo})")
    fig.update_layout(height=400, xaxis_title="Año", yaxis_title="Cantidad de Estudiantes", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_inscripciones_cuatrimestre(df_evolucion):
    if df_evolucion.empty: return crear_grafico_vacio("Inscripciones 2do Cuatrimestre")
    df_melted = df_evolucion.melt(id_vars=['Inscripciones'], value_vars=['2022', '2023', '2024', '2025'], var_name='Año', value_name='Estudiantes')
    df_melted.columns = ['Carrera', 'Año', 'Estudiantes']
    fig = px.bar(df_melted, x='Año', y='Estudiantes', color='Carrera', color_discrete_map=COLORES_CARRERAS, title="📅 Inscripciones 2do Cuatrimestre por Año")
    fig.update_layout(height=400, xaxis_title="Año", yaxis_title="Cantidad de Inscripciones", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_cpu_materias(df_cpu):
    if df_cpu.empty: return crear_grafico_vacio("CPU: Inscripciones por Materias")
    fig = px.bar(df_cpu, x='Inscriptos al CPU', y='Inscriptos', color_discrete_sequence=['#8200e1'], text='Inscriptos', title="📚 CPU: Inscripciones por Cantidad de Materias")
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title="Cantidad de Materias", yaxis_title="Cantidad de Inscriptos", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_egresados_2024(df):
    if df.empty: return crear_grafico_vacio("Egresados por Carrera 2024")
    df_plot = df.sort_values('Cantidad', ascending=True)
    fig = px.bar(df_plot, x='Cantidad', y='Carrera', orientation='h', title='🎓 Egresados por Carrera 2024', labels={'Cantidad': 'Cantidad de Egresados', 'Carrera': 'Carrera'}, color='Carrera', color_discrete_map=COLORES_CARRERAS, text='Cantidad')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, xaxis_title="Cantidad de Egresados", yaxis_title="Carrera", plot_bgcolor='white', showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_cantidad_graduados_por_plan(df):
    if df.empty: return crear_grafico_vacio("Graduados por Plan")
    fig = px.bar(df, x='Carrera', y='Graduados', color='Plan', title='👨‍🎓 Cantidad de graduados por carrera y plan', labels={'Graduados': 'Cantidad de Egresados', 'Carrera': 'Carrera'}, orientation='v', color_discrete_map=COLORES_PLANES, barmode='group', text='Graduados')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, xaxis_title="Carrera", yaxis_title="Cantidad de Egresados", plot_bgcolor='white', showlegend=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_tasa_graduacion(df):
    if df.empty: return crear_grafico_vacio("Tasa de graduación")
    df_plot = df[df['Tasa'] > 0]
    fig = px.bar(df_plot, x='Carrera', y='Tasa', color='Plan', title='📊 Tasa de graduación', labels={'Tasa': 'Tasa de Graduación (%)', 'Carrera': 'Carrera'}, barmode='group', orientation='v', color_discrete_map=COLORES_PLANES, text='Tasa')
    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%')
    fig.update_layout(height=400, xaxis_title="Carrera", yaxis_title="Tasa de Graduación (%)", yaxis_range=[0, df_plot['Tasa'].max() * 1.15], plot_bgcolor='white', showlegend=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_duracion_carrera(df):
    if df.empty: return crear_grafico_vacio("Duración Promedio de Carrera")
    df_plot = df[['Carrera - Plan', 'Duración promedio']].copy()
    df_plot.columns = ['Carrera', 'Duración']
    df_plot = df_plot.sort_values('Duración', ascending=True)
    fig = px.bar(df_plot, x='Duración', y='Carrera', title='⏳ Duración Promedio de la Carrera (Total)', labels={'Duración': 'Años', 'Carrera': 'Carrera y Plan'}, text='Duración')
    fig.update_traces(texttemplate='%{text:.1f} años', textposition='outside')
    fig.update_layout(height=400, xaxis_title="Duración promedio en años", yaxis_title=None, plot_bgcolor='white', showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# --- Estilos ---
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#8200e1", # Un color oscuro
    "color": "white",
}

CONTENT_STYLE = {
    "marginLeft": "16rem",
    "padding": "2rem 1rem",
}

# --- Layout de la App ---
sidebar = html.Div(
    [
        html.Img(src="https://unsam.edu.ar/img/logo_eeyn.png", style={'width': '200px', 'margin-bottom': '20px'}),
        html.Hr(style={'borderColor': 'white'}),
        html.H4("Menú"),
        dcc.Link('👨‍🎓 Inscripciones', href='/inscripciones', style={'color': 'white', 'display': 'block', 'margin': '5px'}),
        dcc.Link('🎓 Egresados', href='/egresados', style={'color': 'white', 'display': 'block', 'margin': '5px'}),
        html.Hr(style={'borderColor': 'white'}),
        html.P("Período: Segundo Cuatrimestre 2025", style={'fontSize': '14px'}),
        html.P(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style={'fontSize': '14px'})
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# --- Layouts de las páginas ---
layout_inscripciones = html.Div([
    html.H1("Inscripción a materias"),
    html.H3("Segundo cuatrimestre 2025"),
    html.Hr(),
    html.Div([
        html.Div([
            html.Label("Filtrar estudiantes por:"),
            dcc.RadioItems(id='filtro-estudiantes-insc', options=[{'label': 'Todas', 'value': 'Todas'}, {'label': 'Grado', 'value': 'Grado'}], value='Todas', labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            dcc.Graph(id='grafico-estudiantes-carrera')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
        html.Div([
            html.Label("Filtrar evolución por:"),
            dcc.RadioItems(id='filtro-evolucion-insc', options=[{'label': 'Todas', 'value': 'Todas'}, {'label': 'Grado', 'value': 'Grado'}], value='Todas', labelStyle={'display': 'inline-block', 'marginRight': '10px'}),
            dcc.Graph(id='grafico-evolucion-temporal')
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
    ], style={'display': 'flex'}),
    html.Div([
        html.Div([dcc.Graph(id='grafico-insc-cuatri')], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
        html.Div([dcc.Graph(id='grafico-cpu')], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
    ], style={'display': 'flex'}),
])

layout_egresados = html.Div([
    html.H1("Análisis de Egresados"),
    html.H3("Indicadores Clave y Visualizaciones"),
    html.Hr(),
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_egresados_2024(df_egresados_2024))], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
        html.Div([dcc.Graph(figure=crear_grafico_cantidad_graduados_por_plan(df_egresados_tasa))], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
    ], style={'display': 'flex'}),
    html.Div([
        html.Div([dcc.Graph(figure=crear_grafico_tasa_graduacion(df_egresados_tasa))], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
        html.Div([dcc.Graph(figure=crear_grafico_duracion_carrera(df_egresados))], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '1%'}),
    ], style={'display': 'flex'}),
])

# --- Callbacks ---
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/egresados':
        return layout_egresados
    return layout_inscripciones

# Callbacks para la página de Inscripciones
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
    if pathname == '/inscripciones':
        return crear_grafico_inscripciones_cuatrimestre(df_todas)
    return crear_grafico_vacio()

@app.callback(Output('grafico-cpu', 'figure'), [Input('url', 'pathname')])
def update_grafico_cpu(pathname):
    if pathname == '/inscripciones':
        return crear_grafico_cpu_materias(df_cpu_mat)
    return crear_grafico_vacio()

# --- Ejecutar la App ---
if __name__ == '__main__':
    app.run(debug=True)

