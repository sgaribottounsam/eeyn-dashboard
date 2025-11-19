import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN GLOBAL DE GRÁFICOS ---
GRAPH_HEIGHT = 350 # Variable para controlar la altura de todos los gráficos

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

def estandarizar_nombres_df(df, mapeo_columnas):
    """Renombra las columnas de un DataFrame según un mapeo, si existen."""
    df_copia = df.copy()
    columnas_a_renombrar = {k: v for k, v in mapeo_columnas.items() if k in df_copia.columns}
    if columnas_a_renombrar:
        df_copia.rename(columns=columnas_a_renombrar, inplace=True)
    return df_copia

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
        height=GRAPH_HEIGHT
    )
    return fig

def crear_grafico_evolucion_egresados(df):
    """
    Crea un gráfico de barras apiladas de egresados por año, con etiquetas de total acumulado.
    """
    if df.empty:
        return crear_grafico_vacio("Evolución de Egresados por Año")

    df_agrupado = df.groupby(['anio_academico', 'propuesta'])['cantidad'].sum().reset_index()
    df_agrupado['anio_academico'] = df_agrupado['anio_academico'].astype(str)
    df_totales = df_agrupado.groupby('anio_academico')['cantidad'].sum().reset_index()

    fig = px.bar(
        df_agrupado, x='anio_academico', y='cantidad', color='propuesta',
        title='🎓 Evolución de Egresados por Año Académico',
        labels={'anio_academico': 'Año Académico', 'cantidad': 'Cantidad de Egresados', 'propuesta': 'Carrera'},
        color_discrete_map=COLORES_CARRERAS,
        text='cantidad'
    )

    fig.update_traces(textposition='inside', textfont=dict(size=10))

    fig.add_trace(go.Scatter(
        x=df_totales['anio_academico'], y=df_totales['cantidad'], text=df_totales['cantidad'],
        mode='text', textposition='top center', textfont=dict(color='black', size=11),
        showlegend=False
    ))

    fig.update_layout(
        height=GRAPH_HEIGHT,
        xaxis_title="Año Académico", yaxis_title="Cantidad de Egresados",
        plot_bgcolor='white', barmode='stack', legend_title_text='Carrera',
        yaxis_range=[0, df_totales['cantidad'].max() * 1.15],
        font=dict(size=10)
    )
    return fig

def crear_grafico_estudiantes_por_carrera(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return crear_grafico_vacio(f"Estudiantes por Carrera 2025 ({filtro_tipo})")
    # Estandarizamos nombres para ser robustos
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})
    
    carreras_2025 = df_plot[['inscripciones', '2025']].copy()
    carreras_2025.columns = ['carrera', 'estudiantes']
    carreras_2025 = carreras_2025.sort_values('estudiantes', ascending=True)
    df_filtered = carreras_2025[carreras_2025['carrera'].isin(COLORES_CARRERAS.keys())]
    fig = px.bar(df_filtered, y='carrera', x='estudiantes', orientation='h', color='carrera',
                 color_discrete_map=COLORES_CARRERAS, text='estudiantes', title=f"👥 Estudiantes por Carrera 2025 ({filtro_tipo})")
    fig.update_traces(textposition='outside', textfont=dict(size=10))
    fig.update_layout(height=GRAPH_HEIGHT, showlegend=False, xaxis_title="Cantidad de Estudiantes", yaxis_title=None, plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_evolucion_temporal(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return crear_grafico_vacio(f"Evolución Temporal ({filtro_tipo})")
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})

    df_melted = df_plot.melt(id_vars=['inscripciones'], value_vars=['2020', '2021', '2022', '2023', '2024', '2025'], var_name='año', value_name='estudiantes')
    df_melted.columns = ['carrera', 'año', 'estudiantes']
    fig = px.line(df_melted, x='año', y='estudiantes', color='carrera', color_discrete_map=COLORES_CARRERAS, markers=True, title=f"📈 Evolución Temporal por Carrera ({filtro_tipo})")
    fig.update_layout(height=GRAPH_HEIGHT, xaxis_title="Año", yaxis_title="Cantidad de Estudiantes", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_inscripciones_cuatrimestre(df_evolucion):
    if df_evolucion.empty: return crear_grafico_vacio("Inscripciones 2do Cuatrimestre")
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})

    df_melted = df_plot.melt(id_vars=['inscripciones'], value_vars=['2022', '2023', '2024', '2025'], var_name='año', value_name='estudiantes')
    df_melted.columns = ['carrera', 'año', 'estudiantes']
    fig = px.bar(df_melted, x='año', y='estudiantes', color='carrera', color_discrete_map=COLORES_CARRERAS, title="📅 Inscripciones 2do Cuatrimestre por Año", text='estudiantes')
    fig.update_traces(textposition='inside', textfont=dict(size=10))
    fig.update_layout(height=GRAPH_HEIGHT, xaxis_title="Año", yaxis_title="Cantidad de Inscripciones", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_cpu_materias(df_cpu):
    if df_cpu.empty: return crear_grafico_vacio("CPU: Inscripciones por Materias")
    df_plot = estandarizar_nombres_df(df_cpu, {'Inscriptos al CPU': 'inscriptos_al_cpu', 'Inscriptos': 'inscriptos'})

    fig = px.bar(df_plot, x='inscriptos_al_cpu', y='inscriptos', color_discrete_sequence=['#8200e1'], text='inscriptos', title="📚 CPU: Inscripciones por Cantidad de Materias")
    fig.update_traces(textposition='outside', textfont=dict(size=10))
    fig.update_layout(height=GRAPH_HEIGHT, showlegend=False, xaxis_title="Cantidad de Materias", yaxis_title="Cantidad de Inscriptos", plot_bgcolor='white', margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_cantidad_graduados_por_plan(df):
    if df.empty: return crear_grafico_vacio("Graduados por Plan")
    # Estandarizamos los nombres de las columnas que vienen del CSV
    df_plot = estandarizar_nombres_df(df, {
        'Carrera': 'propuesta', 'Plan': 'plan', 'Graduados': 'cantidad'
    })

    # Calcular el total por carrera para ordenar
    total_por_carrera = df_plot.groupby('propuesta')['cantidad'].sum().sort_values(ascending=False).index

    color_map = {}
    for carrera in df_plot['propuesta'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc')
        color_map[f"{carrera} - Plan Nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = darken_color(base_color, 0.7)
    df_plot['carrera_y_plan'] = df_plot['propuesta'] + " - " + df_plot['plan']
    
    # Ordenar para apilar correctamente (Viejo abajo, Nuevo arriba)
    df_plot.sort_values(by='carrera_y_plan', ascending=False, inplace=True)

    fig = px.bar(df_plot, x='propuesta', y='cantidad', color='carrera_y_plan',
                 title='👨‍🎓 Cantidad de graduados por carrera y plan',
                 labels={'cantidad': 'Cantidad de Egresados', 'propuesta': 'Carrera', 'carrera_y_plan': 'Carrera y Plan'},
                 orientation='v', color_discrete_map=color_map, barmode='stack', text='cantidad',
                 category_orders={'propuesta': total_por_carrera})
    
    fig.update_traces(textposition='inside', textfont=dict(size=10))

    # Aumentar el tamaño de la fuente para carreras específicas
    for trace in fig.data:
        if 'LI-LECO-P' in trace.name or 'CP-CCCP-PC' in trace.name:
            trace.textfont.size = 14

    fig.update_layout(height=GRAPH_HEIGHT, xaxis_title="Carrera", yaxis_title="Cantidad de Egresados", plot_bgcolor='white', showlegend=True, margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_tasa_graduacion(df):
    if df.empty: return crear_grafico_vacio("Tasa de graduación")
    # Estandarizamos los nombres de las columnas
    df_plot = estandarizar_nombres_df(df, {
        'Carrera': 'propuesta', 'Plan': 'plan', 'Tasa': 'tasa'
    })
    
    df_plot = df_plot[df_plot['tasa'] > 0].copy()
    color_map = {}
    for carrera in df_plot['propuesta'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc')
        color_map[f"{carrera} - Plan Nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = darken_color(base_color, 0.7)
    df_plot['carrera_y_plan'] = df_plot['propuesta'] + " - " + df_plot['plan']
    fig = px.bar(df_plot, x='propuesta', y='tasa', color='carrera_y_plan',
                 title='📊 Tasa de graduación',
                 labels={'tasa': 'Tasa de Graduación (%)', 'propuesta': 'Carrera', 'carrera_y_plan': 'Carrera y Plan'},
                 barmode='group', orientation='v', color_discrete_map=color_map, text='tasa')
    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%', textfont=dict(size=10))
    fig.update_layout(height=GRAPH_HEIGHT, xaxis_title="Carrera", yaxis_title="Tasa de Graduación (%)", yaxis_range=[0, df_plot['tasa'].max() * 1.15], plot_bgcolor='white', showlegend=True, margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

def crear_grafico_duracion_carrera(df):
    if df.empty: return crear_grafico_vacio("Duración Promedio de Carrera")
    # Estandarizamos los nombres de las columnas
    df_plot = estandarizar_nombres_df(df, {
        'Carrera - Plan': 'carrera_plan', 'Duración promedio': 'duracion_promedio'
    })

    df_plot = df_plot[['carrera_plan', 'duracion_promedio']].copy()
    df_plot.columns = ['carrera', 'duracion']
    df_plot = df_plot.sort_values('duracion', ascending=True)
    fig = px.bar(df_plot, x='duracion', y='carrera', title='⏳ Duración Promedio de la Carrera (Total)', labels={'duracion': 'Años', 'carrera': 'Carrera y Plan'}, text='duracion')
    fig.update_traces(texttemplate='%{text:.1f} años', textposition='inside', textfont=dict(size=10))
    fig.update_layout(height=GRAPH_HEIGHT, xaxis_title="Duración promedio en años", yaxis_title=None, plot_bgcolor='white', showlegend=False, margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))
    return fig

# --- Gráficos para la página de Inscripciones a Carreras ---

def crear_grafico_evolucion_inscriptos_diarios(df):
    """Crea un gráfico de líneas con la evolución de inscriptos por día."""
    if df.empty:
        return crear_grafico_vacio("Evolución de Inscriptos por Día")
    
    fig = px.line(df, x='fecha_insc', y='cantidad', title='📈 Evolución de Inscriptos por Día',
                  labels={'fecha_insc': 'Fecha', 'cantidad': 'Inscriptos'}, markers=True)
    fig.update_layout(height=GRAPH_HEIGHT, plot_bgcolor='white')
    return fig

def crear_grafico_comparativa_inscriptos_carrera(df):
    """Crea un gráfico de barras agrupadas para comparar preinscriptos e inscriptos por carrera."""
    if df.empty:
        return crear_grafico_vacio("Comparativa Inscriptos vs. Preinscriptos")

    df_melted = df.melt(id_vars='carrera', value_vars=['preinscriptos', 'inscriptos'],
                        var_name='tipo', value_name='cantidad')

    fig = px.bar(df_melted, x='carrera', y='cantidad', color='tipo', barmode='group',
                 title='👥 Comparativa Inscriptos vs. Preinscriptos por Carrera',
                 labels={'carrera': 'Carrera', 'cantidad': 'Cantidad', 'tipo': 'Estado'},
                 text='cantidad')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=GRAPH_HEIGHT, plot_bgcolor='white')
    return fig

def crear_grafico_distribucion_preinscriptos_estado(df):
    """Crea un gráfico de torta para ver la distribución de preinscriptos por estado."""
    if df.empty:
        return crear_grafico_vacio("Distribución de Preinscriptos por Estado")

    fig = px.pie(df, names='estado', values='cantidad', 
                 title='📊 Distribución de Preinscriptos por Estado',
                 hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=GRAPH_HEIGHT, showlegend=False)
    return fig

def crear_grafico_inscriptos_grado_por_dia(df):
    """
    Crea un gráfico de líneas que muestra el total acumulado de inscriptos de grado por día.
    Compara los años a partir de 2024 en el período del 1 de octubre al 15 de noviembre.
    """
    if df.empty:
        return crear_grafico_vacio("No hay datos de inscripciones de grado para mostrar.")

    fig = go.Figure()

    # La data ya viene filtrada y agrupada desde la consulta SQL
    df['anio'] = df['anio'].astype(str)
    df_pivot = df.pivot_table(index='dia_mes', columns='anio', values='cantidad', aggfunc='sum').fillna(0)
    
    # Asegurar que el orden del eje X sea cronológico y calcular el acumulado
    df_pivot.sort_index(inplace=True)
    df_cumulative = df_pivot.cumsum()

    for year in sorted(df_cumulative.columns):
        # User request: 2026 solid, others dotted.
        line_style = 'solid' if year == '2026' else 'dot'
        
        x_axis_labels = [pd.to_datetime(f"1900-{day_month}").strftime('%d-%b') for day_month in df_cumulative.index]

        fig.add_trace(go.Scatter(
            x=x_axis_labels,
            y=df_cumulative[year],
            mode='lines+markers',
            name=year,
            line=dict(dash=line_style)
        ))

    fig.update_layout(
        title_text='Inscriptos de Grado por Día (Acumulado)',
        xaxis_title='Fecha',
        yaxis_title='Total Acumulado de Inscriptos',
        legend_title='Año',
        height=GRAPH_HEIGHT,
        plot_bgcolor='white',
        font=dict(size=10)
    )

    return fig

def crear_grafico_inscripciones_por_anio_carrera(df):
    """
    Crea un gráfico de barras apiladas de inscripciones por año y carrera.
    """
    if df.empty:
        return crear_grafico_vacio("No hay datos de inscripciones por año y carrera.")

    # Calcular totales por año para las etiquetas
    df_totales = df.groupby('anio')['cantidad'].sum().reset_index()

    fig = px.bar(
        df,
        x='anio',
        y='cantidad',
        color='carrera_codigo', # Usa el código para el mapeo de colores
        hover_name='carrera_nombre', # Muestra el nombre completo en el hover
        barmode='stack',
        title='Inscripciones de Grado por Año y Carrera',
        labels={'anio': 'Año', 'cantidad': 'Cantidad de Inscriptos', 'carrera_codigo': 'Carrera'},
        color_discrete_map=COLORES_CARRERAS,
        text='cantidad'
    )
    fig.update_traces(textposition='inside', textfont=dict(size=10))

    # Agregar etiquetas con el total
    fig.add_trace(go.Scatter(
        x=df_totales['anio'],
        y=df_totales['cantidad'],
        text=df_totales['cantidad'],
        mode='text',
        textposition='top center',
        textfont=dict(color='black', size=11),
        showlegend=False
    ))

    fig.update_layout(
        height=GRAPH_HEIGHT,
        plot_bgcolor='white',
        yaxis_range=[0, df_totales['cantidad'].max() * 1.15], # Ajustar el rango del eje Y
        font=dict(size=10)
    )
    return fig

def crear_grafico_documentacion_por_dia(df):
    """
    Crea un gráfico de barras apiladas de la recepción de documentación por día.
    """
    if df.empty:
        return crear_grafico_vacio("Evolución de la Recepción de Documentación")

    # Los datos ya vienen pivotados desde el loader
    # Columnas esperadas: fecha, Aprobada, Rechazada, Duplicado, Revisar
    
    # Calcular el total por día
    df['Total'] = df[['Aprobada', 'Rechazada', 'Duplicado', 'Revisar']].sum(axis=1)

    fig = px.bar(
        df,
        x='fecha',
        y=['Aprobada', 'Rechazada', 'Duplicado', 'Revisar'],
        title='📂 Evolución de la Recepción de Documentación por Día',
        labels={'fecha': 'Fecha', 'value': 'Cantidad de Documentos', 'variable': 'Estado'},
        barmode='stack',
        color_discrete_map={
            'Aprobada': '#28a745',
            'Rechazada': '#dc3545',
            'Duplicado': '#007bff',  # Azul
            'Revisar': '#ffc107'   # Amarillo
        },
        text_auto=True
    )
    fig.update_traces(textfont_size=10)

    # Agregar etiquetas con el total
    fig.add_trace(go.Scatter(
        x=df['fecha'],
        y=df['Total'],
        text=df['Total'],
        mode='text',
        textposition='top center',
        textfont=dict(color='black', size=11),
        showlegend=False
    ))

    fig.update_layout(
        height=GRAPH_HEIGHT,
        plot_bgcolor='white',
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Documentos",
        legend_title_text='Estado',
        yaxis_range=[0, df['Total'].max() * 1.15], # Ajustar el rango del eje Y
        font=dict(size=10)
    )
    
    return fig

def crear_grafico_inscriptos_grado_y_pregrado_por_dia(df):
    """
    Crea un gráfico de barras que muestra el total de inscriptos de grado y pregrado por día.
    Compara los años a partir de 2024 en el período del 1 de octubre al 15 de noviembre.
    """
    if df.empty:
        return crear_grafico_vacio("No hay datos de inscripciones para mostrar.")

    fig = go.Figure()

    df['anio'] = df['anio'].astype(str)
    df_pivot = df.pivot_table(index='dia_mes', columns='anio', values='cantidad', aggfunc='sum').fillna(0)
    
    df_pivot.sort_index(inplace=True)

    for year in sorted(df_pivot.columns):
        x_axis_labels = [pd.to_datetime(f"1900-{day_month}").strftime('%d-%b') for day_month in df_pivot.index]

        fig.add_trace(go.Bar(
            x=x_axis_labels,
            y=df_pivot[year],
            name=year,
            text=df_pivot[year],
            textposition='auto'
        ))

    fig.update_traces(textfont_size=10)

    fig.update_layout(
        title_text='Inscriptos de Grado y Pregrado por Día',
        xaxis_title='Fecha',
        yaxis_title='Total de Inscriptos',
        legend_title='Año',
        height=GRAPH_HEIGHT,
        plot_bgcolor='white',
        barmode='group',
        font=dict(size=10)
    )

    return fig

def crear_grafico_egresados_por_tipo(df, tipo):
    """
    Crea un gráfico de barras de egresados por carrera para un tipo específico (Grado/Posgrado).
    """
    if df.empty:
        return crear_grafico_vacio(f"Egresados de {tipo}")

    total_egresados = df['cantidad'].sum()
    titulo = f'Egresados {tipo} (Total: {total_egresados})'

    df_sorted = df.sort_values(by='cantidad', ascending=False)

    fig = px.bar(
        df_sorted,
        x='propuesta',
        y='cantidad',
        orientation='v',
        title=titulo,
        labels={'propuesta': 'Carrera', 'cantidad': 'Cantidad de Egresados'},
        text='cantidad',
        color='propuesta',
        color_discrete_map=COLORES_CARRERAS
    )

    fig.update_traces(textposition='inside')
    fig.update_layout(
        height=GRAPH_HEIGHT,
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title='Carrera'
    )

    return fig

def crear_grafico_estudiantes_activos(df):
    """
    Crea un gráfico de columnas de la evolución de estudiantes activos por año y tipo.
    """
    if df.empty:
        return crear_grafico_vacio("Evolución de Estudiantes Activos")

    fig = px.bar(
        df,
        x='anio',
        y='total_estudiantes',
        color='tipo',
        barmode='group',
        text_auto=True,
        title='Evolución de Estudiantes Activos por Año y Tipo'
    )
    
    fig.update_traces(textposition='inside')
    
    fig.update_layout(
        height=GRAPH_HEIGHT,
        xaxis_title="Año",
        yaxis_title="Cantidad de Estudiantes",
        plot_bgcolor='white',
        legend_title_text='Tipo de Carrera'
    )
    
    return fig
