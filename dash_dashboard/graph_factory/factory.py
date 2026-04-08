import pandas as pd
import plotly.graph_objects as go
from .theme import COLORES_CARRERAS, lighten_color
from .builders import build_empty_chart, build_bar_chart, build_line_chart, build_pie_chart
from utils.data_utils import estandarizar_nombres_df

def crear_grafico_vacio(titulo="Datos no disponibles"):
    return build_empty_chart(titulo)

def crear_grafico_evolucion_egresados(df):
    if df.empty: return build_empty_chart("Evolución de Egresados por Año")

    df_agrupado = df.groupby(['anio_academico', 'propuesta'])['cantidad'].sum().reset_index()
    df_agrupado['anio_academico'] = df_agrupado['anio_academico'].astype(str)
    
    fig = build_bar_chart(
        df_agrupado, x='anio_academico', y='cantidad', color='propuesta',
        title='Evolución de Egresados por Año Académico',
        labels={'anio_academico': 'Año Académico', 'cantidad': 'Cantidad de Egresados', 'propuesta': 'Carrera'},
        color_map=COLORES_CARRERAS, barmode='stack', text='cantidad',
        apply_zoom_2020=True
    )
    
    df_totales = df_agrupado.groupby('anio_academico')['cantidad'].sum().reset_index()
    fig.add_trace(go.Scatter(
        x=df_totales['anio_academico'], y=df_totales['cantidad'], text=df_totales['cantidad'],
        mode='text', textposition='top center', textfont=dict(color='black', size=11),
        showlegend=False
    ))
    fig.update_layout(yaxis_range=[0, df_totales['cantidad'].max() * 1.15])
    return fig

def crear_grafico_estudiantes_por_carrera(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return build_empty_chart(f"Estudiantes por Carrera 2025 ({filtro_tipo})")
    
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})
    carreras_2025 = df_plot[['inscripciones', '2025']].copy()
    carreras_2025.columns = ['carrera', 'estudiantes']
    carreras_2025 = carreras_2025.sort_values('estudiantes', ascending=True)
    df_filtered = carreras_2025[carreras_2025['carrera'].isin(COLORES_CARRERAS.keys())]
    
    fig = build_bar_chart(
        df_filtered, x='estudiantes', y='carrera', color='carrera',
        title=f"Estudiantes por Carrera 2025 ({filtro_tipo})",
        labels={'carrera': 'Carrera', 'estudiantes': 'Cantidad de Estudiantes'},
        color_map=COLORES_CARRERAS, orientation='h', text='estudiantes'
    )
    fig.update_layout(showlegend=False, yaxis_title=None)
    return fig

def crear_grafico_evolucion_temporal(df_evolucion, filtro_tipo):
    if df_evolucion.empty: return build_empty_chart(f"Evolución Temporal ({filtro_tipo})")
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})

    df_melted = df_plot.melt(id_vars=['inscripciones'], value_vars=['2020', '2021', '2022', '2023', '2024', '2025'], var_name='año', value_name='estudiantes')
    df_melted.columns = ['carrera', 'año', 'estudiantes']
    
    return build_line_chart(
        df_melted, x='año', y='estudiantes', color='carrera', 
        title=f"Evolución Temporal por Carrera ({filtro_tipo})",
        labels={'año': 'Año', 'estudiantes': 'Cantidad de Estudiantes'},
        color_map=COLORES_CARRERAS, apply_zoom_2020=True
    )

def crear_grafico_inscripciones_cuatrimestre(df_evolucion):
    if df_evolucion.empty: return build_empty_chart("Inscripciones 2do Cuatrimestre")
    df_plot = estandarizar_nombres_df(df_evolucion, {'Inscripciones': 'inscripciones'})

    df_melted = df_plot.melt(id_vars=['inscripciones'], value_vars=['2022', '2023', '2024', '2025'], var_name='año', value_name='estudiantes')
    df_melted.columns = ['carrera', 'año', 'estudiantes']
    
    return build_bar_chart(
        df_melted, x='año', y='estudiantes', color='carrera',
        title="Inscripciones 2do Cuatrimestre por Año",
        labels={'año': 'Año', 'estudiantes': 'Cantidad de Inscripciones'},
        barmode='group', text='estudiantes', color_map=COLORES_CARRERAS, apply_zoom_2020=True
    )

def crear_grafico_cpu_materias(df_cpu):
    if df_cpu.empty: return build_empty_chart("CPU: Inscripciones por Materias")
    df_plot = estandarizar_nombres_df(df_cpu, {'Inscriptos al CPU': 'inscriptos_al_cpu', 'Inscriptos': 'inscriptos'})

    fig = build_bar_chart(
        df_plot, x='inscriptos_al_cpu', y='inscriptos', text='inscriptos',
        title="CPU: Inscripciones por Cantidad de Materias",
        labels={'inscriptos_al_cpu': 'Cantidad de Materias', 'inscriptos': 'Cantidad de Inscriptos'}
    )
    fig.update_traces(marker_color='#8200e1')
    fig.update_layout(showlegend=False)
    return fig

def crear_grafico_cantidad_graduados_por_plan(df):
    if df.empty: return build_empty_chart("Graduados por Plan")
    df_plot = estandarizar_nombres_df(df, {'Carrera': 'propuesta', 'Plan': 'plan', 'Graduados': 'cantidad'})
    total_por_carrera = df_plot.groupby('propuesta')['cantidad'].sum().sort_values(ascending=False).index

    color_map = {}
    for carrera in df_plot['propuesta'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc')
        color_map[f"{carrera} - Plan Nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = lighten_color(base_color, 0.4)
    df_plot['carrera_y_plan'] = df_plot['propuesta'] + " - " + df_plot['plan']
    df_plot.sort_values(by='carrera_y_plan', ascending=False, inplace=True)

    fig = build_bar_chart(
        df_plot, x='propuesta', y='cantidad', color='carrera_y_plan',
        title='Cantidad de graduados por carrera y plan',
        labels={'cantidad': 'Cantidad de Egresados', 'propuesta': 'Carrera', 'carrera_y_plan': 'Carrera y Plan'},
        color_map=color_map, barmode='stack', text='cantidad', category_orders={'propuesta': total_por_carrera}
    )
    
    for trace in fig.data:
        if 'LI-LECO-P' in trace.name or 'CP-CCCP-PC' in trace.name:
            trace.textfont.size = 14
    return fig

def crear_grafico_tasa_graduacion(df):
    if df.empty: return build_empty_chart("Tasa de graduación")
    df_plot = estandarizar_nombres_df(df, {'Carrera': 'propuesta', 'Plan': 'plan', 'Tasa': 'tasa'})
    df_plot = df_plot[df_plot['tasa'] > 0].copy()
    
    color_map = {}
    for carrera in df_plot['propuesta'].unique():
        base_color = COLORES_CARRERAS.get(carrera, '#cccccc')
        color_map[f"{carrera} - Plan Nuevo"] = base_color
        color_map[f"{carrera} - Plan Viejo"] = lighten_color(base_color, 0.4)
    df_plot['carrera_y_plan'] = df_plot['propuesta'] + " - " + df_plot['plan']
    
    fig = build_bar_chart(
        df_plot, x='propuesta', y='tasa', color='carrera_y_plan',
        title='Tasa de graduación', barmode='group', color_map=color_map,
        labels={'tasa': 'Tasa de Graduación (%)', 'propuesta': 'Carrera', 'carrera_y_plan': 'Carrera y Plan'},
        text='tasa', text_template='%{text:.2f}%', forced_text_position='outside'
    )
    fig.update_layout(yaxis_range=[0, df_plot['tasa'].max() * 1.15])
    return fig

def crear_grafico_duracion_carrera(df):
    if df.empty: return build_empty_chart("Duración Promedio de Carrera")
    df_plot = estandarizar_nombres_df(df, {'Carrera - Plan': 'carrera_plan', 'Duración promedio': 'duracion_promedio'})
    df_plot = df_plot[['carrera_plan', 'duracion_promedio']].copy()
    df_plot.columns = ['carrera', 'duracion']
    df_plot = df_plot.sort_values('duracion', ascending=True)
    
    fig = build_bar_chart(
        df_plot, x='duracion', y='carrera', text='duracion', orientation='h',
        title='Duración Promedio de la Carrera (Total)',
        labels={'duracion': 'Años', 'carrera': 'Carrera y Plan'},
        text_template='%{text:.1f} años', forced_text_position='inside'
    )
    fig.update_layout(xaxis_title="Duración promedio en años", yaxis_title=None, showlegend=False)
    return fig

def crear_grafico_evolucion_inscriptos_diarios(df):
    if df.empty: return build_empty_chart("Evolución de Inscriptos por Día")
    return build_line_chart(
        df, x='fecha_insc', y='cantidad', title='Evolución de Inscriptos por Día',
        labels={'fecha_insc': 'Fecha', 'cantidad': 'Inscriptos'}
    )

def crear_grafico_comparativa_inscriptos_carrera(df):
    if df.empty: return build_empty_chart("Comparativa Inscriptos vs. Preinscriptos")
    df_melted = df.melt(id_vars='carrera', value_vars=['preinscriptos', 'inscriptos'], var_name='tipo', value_name='cantidad')
    return build_bar_chart(
        df_melted, x='carrera', y='cantidad', color='tipo', barmode='group', text='cantidad',
        title='Comparativa Inscriptos vs. Preinscriptos por Carrera',
        labels={'carrera': 'Carrera', 'cantidad': 'Cantidad', 'tipo': 'Estado'}
    )

def crear_grafico_distribucion_preinscriptos_estado(df):
    if df.empty: return build_empty_chart("Distribución de Preinscriptos por Estado")
    fig = build_pie_chart(
        df, names='estado', values='cantidad', 
        title='Distribución de Preinscriptos por Estado'
    )
    fig.update_layout(showlegend=False)
    return fig

def crear_grafico_inscriptos_grado_por_dia(df):
    if df.empty: return build_empty_chart("No hay datos de inscripciones de grado para mostrar.")
    
    from .builders import apply_standard_layout
    fig = go.Figure()
    
    df['anio'] = df['anio'].astype(str)
    df_pivot = df.pivot_table(index='dia_mes', columns='anio', values='cantidad', aggfunc='sum').fillna(0)
    df_pivot.sort_index(inplace=True)
    df_cumulative = df_pivot.cumsum()

    for year in sorted(df_cumulative.columns):
        line_style = 'solid' if year == '2026' else 'dot'
        x_axis_labels = [pd.to_datetime(f"1900-{day_month}").strftime('%d-%b') for day_month in df_cumulative.index]
        fig.add_trace(go.Scatter(
            x=x_axis_labels, y=df_cumulative[year], mode='lines+markers', name=year, line=dict(dash=line_style),
            text=df_cumulative[year], textposition='top center'
        ))

    fig = apply_standard_layout(fig)
    fig.update_layout(title_text='<b>Inscriptos de Grado por Día (Acumulado)</b>', xaxis_title='Fecha', yaxis_title='Total Acumulado de Inscriptos', legend_title='Año')
    return fig

def crear_grafico_inscripciones_por_anio_carrera(df):
    if df.empty: return build_empty_chart("No hay datos de inscripciones por año y carrera.")
    df_totales = df.groupby('anio')['cantidad'].sum().reset_index()

    fig = build_bar_chart(
        df, x='anio', y='cantidad', color='carrera_codigo', hover_name='carrera_nombre',
        title='Inscripciones de Grado por Año y Carrera', barmode='stack', text='cantidad',
        labels={'anio': 'Año', 'cantidad': 'Cantidad de Inscriptos', 'carrera_codigo': 'Carrera'}, 
        color_map=COLORES_CARRERAS, apply_zoom_2020=True
    )

    fig.add_trace(go.Scatter(
        x=df_totales['anio'], y=df_totales['cantidad'], text=df_totales['cantidad'],
        mode='text', textposition='top center', textfont=dict(color='black', size=11), showlegend=False
    ))
    fig.update_layout(yaxis_range=[0, df_totales['cantidad'].max() * 1.15])
    return fig

def crear_grafico_documentacion_por_dia(df):
    if df.empty: return build_empty_chart("Evolución de la Recepción de Documentación")

    df['Total'] = df[['Aprobada', 'Rechazada', 'Duplicado', 'Revisar']].sum(axis=1)

    fig = build_bar_chart(
        df, x='fecha', y=['Aprobada', 'Rechazada', 'Duplicado', 'Revisar'],
        title='Evolución de la Recepción de Documentación por Día', barmode='stack',
        labels={'fecha': 'Fecha', 'value': 'Cantidad de Documentos', 'variable': 'Estado'},
        color_map={'Aprobada': '#28a745', 'Rechazada': '#dc3545', 'Duplicado': '#007bff', 'Revisar': '#ffc107'}
    )

    fig.add_trace(go.Scatter(
        x=df['fecha'], y=df['Total'], text=df['Total'], mode='text', 
        textposition='top center', textfont=dict(color='black', size=11), showlegend=False
    ))
    fig.update_layout(yaxis_range=[0, df['Total'].max() * 1.15], legend_title_text='Estado')
    return fig

def crear_grafico_inscriptos_grado_y_pregrado_por_dia(df):
    if df.empty: return build_empty_chart("No hay datos de inscripciones para mostrar.")
    
    from .builders import apply_standard_layout
    fig = go.Figure()

    df['anio'] = df['anio'].astype(str)
    df_pivot = df.pivot_table(index='dia_mes', columns='anio', values='cantidad', aggfunc='sum').fillna(0)
    df_pivot.sort_index(inplace=True)

    for year in sorted(df_pivot.columns):
        x_axis_labels = [pd.to_datetime(f"1900-{day_month}").strftime('%d-%b') for day_month in df_pivot.index]
        fig.add_trace(go.Bar(
            x=x_axis_labels, y=df_pivot[year], name=year, text=df_pivot[year], textposition='auto'
        ))

    fig = apply_standard_layout(fig)
    fig.update_traces(textfont_size=10)
    fig.update_layout(title_text='<b>Inscriptos de Grado y Pregrado por Día</b>', xaxis_title='Fecha', 
                      yaxis_title='Total de Inscriptos', legend_title='Año', barmode='group')
    return fig

def crear_grafico_egresados_por_tipo(df, tipo):
    if df.empty: return build_empty_chart(f"Egresados de {tipo}")
    df_sorted = df.sort_values(by='cantidad', ascending=False)
    
    fig = build_bar_chart(
        df_sorted, x='propuesta', y='cantidad', color='propuesta', text='cantidad',
        title=f"Egresados {tipo} (Total: {df['cantidad'].sum()})", 
        labels={'propuesta': 'Carrera', 'cantidad': 'Cantidad de Egresados'},
        color_map=COLORES_CARRERAS
    )
    fig.update_layout(showlegend=False)
    return fig

def crear_grafico_estudiantes_activos(df):
    if df.empty: return build_empty_chart("Evolución de Estudiantes Activos")

    return build_bar_chart(
        df, x='anio', y='total_estudiantes', color='tipo', barmode='group', text='total_estudiantes',
        title='Evolución de Estudiantes Activos por Año y Tipo',
        labels={'anio': 'Año', 'total_estudiantes': 'Cantidad de Estudiantes'},
        apply_zoom_2020=True
    )
