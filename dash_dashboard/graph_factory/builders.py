# dash_dashboard/graph_factory/builders.py
import plotly.express as px
import plotly.graph_objects as go
from .theme import COMMON_LAYOUT, COLORES_CARRERAS

def apply_standard_layout(fig):
    """Aplica el diseño base COMMON_LAYOUT y ajustes extra a una figura Plotly."""
    layout_updates = COMMON_LAYOUT.copy()
    fig.update_layout(**layout_updates)
    
    # Forzar explícitamente la leyenda abajo usando kwargs directos de Plotly 
    # por si dict() en COMMON_LAYOUT es omitido por plotly express
    fig.update_layout(
        legend_orientation="h", 
        legend_yanchor="top", 
        legend_y=-0.25, 
        legend_xanchor="center", 
        legend_x=0.5
    )
    return fig

def set_zoom_2020(fig, df, x):
    # Suspendido temporalmente el zoom según requerimiento
    return fig

def build_empty_chart(title="Datos no disponibles"):
    """Crea un gráfico vacío estándar para usar cuando no hay datos."""
    if not title.startswith("<b>"):
        title = f"<b>{title}</b>"
    fig = px.bar()
    fig.update_layout(
        **COMMON_LAYOUT,
        title=title,
        xaxis={'visible': False}, yaxis={'visible': False},
        annotations=[{
            'text': 'No se pudieron cargar los datos para este gráfico.',
            'xref': 'paper', 'yref': 'paper',
            'showarrow': False, 'font': {'size': 14}
        }]
    )
    return fig

def build_bar_chart(df, x, y, title, labels=None, color=None, text=None, barmode='relative', 
                    orientation='v', color_map=None, category_orders=None, hover_name=None, 
                    apply_zoom_2020=False, text_template=None, forced_text_position=None):
    """Constructor genérico para gráficos de barras Plotly Express."""
    if not title.startswith("<b>"):
        title = f"<b>{title}</b>"
        
    fig = px.bar(
        df, x=x, y=y, color=color, title=title, labels=labels,
        text=text, barmode=barmode, orientation=orientation,
        color_discrete_map=color_map, category_orders=category_orders,
        hover_name=hover_name, text_auto=True if not text else False
    )
    
    # Lógica centralizada para etiquetas y leyenda (requisitos del usuario)
    text_pos = forced_text_position if forced_text_position else ('outside' if barmode == 'group' or orientation == 'h' else 'inside')
    
    trace_updates = dict(textposition=text_pos, textfont=dict(size=10))
    if text_template:
        trace_updates['texttemplate'] = text_template

    fig.update_traces(**trace_updates)
    fig = apply_standard_layout(fig)
    if apply_zoom_2020:
        fig = set_zoom_2020(fig, df, x)
    return fig

def build_line_chart(df, x, y, title, labels=None, color=None, color_map=None, markers=True, apply_zoom_2020=False):
    """Constructor genérico para gráficos de líneas Plotly Express."""
    if not title.startswith("<b>"):
        title = f"<b>{title}</b>"
        
    fig = px.line(
        df, x=x, y=y, color=color, title=title, labels=labels,
        markers=markers, color_discrete_map=color_map
    )
    
    # En líneas forzamos la muestra de valores (etiquetas en nodos si es necesario)
    fig.update_traces(textposition='top center') 
    fig = apply_standard_layout(fig)
    if apply_zoom_2020:
        fig = set_zoom_2020(fig, df, x)
    return fig

def build_pie_chart(df, names, values, title, hole=0.3, color_map=None):
    """Constructor genérico para gráficos de torta Plotly Express."""
    if not title.startswith("<b>"):
        title = f"<b>{title}</b>"
        
    fig = px.pie(
        df, names=names, values=values, title=title, hole=hole, color=names, color_discrete_map=color_map
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig = apply_standard_layout(fig)
    # Excepción explícita para la leyenda en pie charts si es necesario, pero usaremos el standard.
    return fig
