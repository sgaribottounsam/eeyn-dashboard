import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # <-- Importamos graph_objects

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    'CP-CCCP-PC': '#5dae8b',
    'LI-LAGE-P': '#f6f49d',
    'LI-LECO-P': '#ff7676',
    'LI-LEDC-P': '#FF8C00',
    'LI-LTUR-P': '#466c95',
    'TE-MPCO-P': '#c5705d',
    'TE-GUIA-P': '#8B4513',
    'CI-EEYN-P': '#8200e1'
}

# --- Funciones de Utilidad ---
def darken_color(hex_color, factor=0.7):
    """Oscurece un color hexadecimal por un factor dado."""
    if hex_color.startswith('#'):
        hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    dark_rgb = tuple(int(c * factor) for c in rgb)
    return f"#{dark_rgb[0]:02x}{dark_rgb[1]:02x}{dark_rgb[2]:02x}"

# --- Funciones de Gráficos ---

def crear_grafico_vacio(titulo="Datos no disponibles"):
    fig = px.bar()
    fig.update_layout(
        title=titulo,
        xaxis={'visible': False}, yaxis={'visible': False},
        annotations=[{
            'text': 'No se pudieron cargar los datos para este gráfico.',
            'xref': 'paper', 'yref': 'paper',
            'showarrow': False, 'font': {'size': 14}
        }],
        plot_bgcolor='white',
        height=400
    )
    return fig

# --- FUNCIÓN CORREGIDA PARA EL GRÁFICO DE EVOLUCIÓN DE EGRESADOS ---
def crear_grafico_evolucion_egresados(df):
    """
    Crea un gráfico de barras apiladas de egresados por año, con etiquetas de total acumulado.
    """
    if df.empty:
        return crear_grafico_vacio("Evolución de Egresados por Año")

    # Agrupamos los datos para sumar las cantidades por año y propuesta.
    df_agrupado = df.groupby(['anio_academico', 'propuesta'])['cantidad'].sum().reset_index()
    df_agrupado['anio_academico'] = df_agrupado['anio_academico'].astype(str)

    # Calculamos el total para cada año académico, que usaremos para las etiquetas.
    df_totales = df_agrupado.groupby('anio_academico')['cantidad'].sum().reset_index()

    # 1. Creamos el gráfico de barras apiladas base.
    fig = px.bar(
        df_agrupado,
        x='anio_academico',
        y='cantidad',
        color='propuesta',
        title='🎓 Evolución de Egresados por Año Académico',
        labels={
            'anio_academico': 'Año Académico',
            'cantidad': 'Cantidad de Egresados',
            'propuesta': 'Carrera'
        },
        color_discrete_map=COLORES_CARRERAS
    )

    # 2. Añadimos una traza de 'scatter' invisible que SÓLO muestra el texto con los totales.
    # Este método es mucho más robusto que las anotaciones.
    fig.add_trace(go.Scatter(
        x=df_totales['anio_academico'],
        y=df_totales['cantidad'],
        text=df_totales['cantidad'],
        mode='text',
        textposition='top center',
        textfont=dict(
            color='black',
            size=11
        ),
        showlegend=False
    ))

    fig.update_layout(
        height=400,
        xaxis_title="Año Académico",
        yaxis_title="Cantidad de Egresados",
        plot_bgcolor='white',
        barmode='stack',
        legend_title_text='Carrera',
        # Aumentamos el rango del eje Y para que las etiquetas quepan bien
        yaxis_range=[0, df_totales['cantidad'].max() * 1.15]
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
    fig.update_layout(height=400, showlegend=False, xaxis_title="Cantidad de Estudiantes", yaxis_title=None, plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20))
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
    fig.update_layout(height=400, xaxis_title="Cantidad de Egresados", yaxis_title=None, plot_bgcolor='white', showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_cantidad_graduados_por_plan(df):
    if df.empty: return crear_grafico_vacio("Graduados por Plan")
    
    df_plot = df.copy()
    color_map = {}
    # Generamos un mapa de colores dinámico basado en la carrera y el plan
    for carrera in df_plot['Carrera'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc') # Color base
        color_map[f"{carrera} - Plan nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = darken_color(base_color, 0.7) # Color oscurecido
    
    # Creamos una columna combinada para usar en la leyenda y el color
    df_plot['Carrera y Plan'] = df_plot['Carrera'] + " - " + df_plot['Plan']

    fig = px.bar(df_plot, x='Carrera', y='Graduados', color='Carrera y Plan',
                 title='👨‍🎓 Cantidad de graduados por carrera y plan',
                 labels={'Graduados': 'Cantidad de Egresados', 'Carrera': 'Carrera', 'Carrera y Plan': 'Carrera y Plan'},
                 orientation='v', color_discrete_map=color_map, barmode='group', text='Graduados')
    
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400, xaxis_title="Carrera", yaxis_title="Cantidad de Egresados", plot_bgcolor='white', showlegend=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def crear_grafico_tasa_graduacion(df):
    if df.empty: return crear_grafico_vacio("Tasa de graduación")
    
    df_plot = df[df['Tasa'] > 0].copy()
    color_map = {}
    # Generamos un mapa de colores dinámico basado en la carrera y el plan
    for carrera in df_plot['Carrera'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc')
        color_map[f"{carrera} - Plan nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = darken_color(base_color, 0.7)

    # Creamos una columna combinada para usar en la leyenda y el color
    df_plot['Carrera y Plan'] = df_plot['Carrera'] + " - " + df_plot['Plan']

    fig = px.bar(df_plot, x='Carrera', y='Tasa', color='Carrera y Plan',
                 title='📊 Tasa de graduación',
                 labels={'Tasa': 'Tasa de Graduación (%)', 'Carrera': 'Carrera', 'Carrera y Plan': 'Carrera y Plan'},
                 barmode='group', orientation='v', color_discrete_map=color_map, text='Tasa')
                 
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

