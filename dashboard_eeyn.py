import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Obsoleto",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    'CP': '#5dae8b',     # Amarillo
    'LAGE': '#f6f49d',   # Azul
    'LECO': '#ff7676',   # Verde
    'LEDC': '#FF8C00',   # Naranja
    'LTUR': '#466c95',   # Rojo
    'MPCC': '#c5705d',   # Celeste
    'GUIA': '#8B4513',   # Marrón
    'CPU': '#D4BDAC'     # Violeta
}

@st.cache_data
def cargar_kpis():
    """Carga los KPIs desde el archivo CSV."""
    try:
        df_kpi = pd.read_csv('KPI_inc_materias.csv', header=None, names=['Indicador', 'Valor'])
        kpis = {}
        for _, row in df_kpi.iterrows():
            kpis[row['Indicador']] = row['Valor']
        return kpis
    except Exception as e:
        st.error(f"Error cargando KPIs: {e}")
        return {}

@st.cache_data
def cargar_evolucion_todas():
    """Carga los datos de evolución de todas las carreras."""
    try:
        df = pd.read_csv('TODAS_evolucion.csv')
        # Limpiar filas vacías
        df = df.dropna(how='all')
        # Filtrar solo filas de carreras (no totales)
        carreras_df = df[~df['Inscripciones'].str.contains('Total', na=False)]
        return carreras_df
    except Exception as e:
        st.error(f"Error cargando evolución todas: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_evolucion_grado():
    """Carga los datos de evolución solo de carreras de grado."""
    try:
        df = pd.read_csv('GRADO_evolucion.csv')
        # Limpiar filas vacías
        df = df.dropna(how='all')
        # Filtrar solo filas de carreras (no totales)
        carreras_df = df[~df['Inscripciones'].str.contains('Total', na=False)]
        return carreras_df
    except Exception as e:
        st.error(f"Error cargando evolución grado: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_cpu_materias():
    """Carga los datos de CPU por cantidad de materias."""
    try:
        df = pd.read_csv('CPU_cantidad_materias.csv')
        return df
    except Exception as e:
        st.error(f"Error cargando CPU materias: {e}")
        return pd.DataFrame()

def crear_grafico_estudiantes_por_carrera(df_evolucion, filtro_tipo):
    """Crea el gráfico de estudiantes por carrera para 2025."""
    try:
        if df_evolucion.empty:
            return None

        # Obtener datos de 2025
        carreras_2025 = df_evolucion[['Inscripciones', '2025']].copy()
        carreras_2025.columns = ['Carrera', 'Estudiantes']
        carreras_2025 = carreras_2025.sort_values('Estudiantes', ascending=True)

        fig = px.bar(
            carreras_2025, 
            y='Carrera', 
            x='Estudiantes',
            orientation='h',
            color='Carrera',
            color_discrete_map=COLORES_CARRERAS,
            text='Estudiantes',
            title=f"👥 Estudiantes por Carrera 2025 ({filtro_tipo})"
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=400, 
            showlegend=False,
            xaxis_title="Cantidad de Estudiantes",
            yaxis_title="Carrera"
        )

        return fig
    except Exception as e:
        st.error(f"Error creando gráfico estudiantes: {e}")
        return None

def crear_grafico_evolucion_temporal(df_evolucion, filtro_tipo):
    """Crea el gráfico de evolución temporal por carrera."""
    try:
        if df_evolucion.empty:
            return None

        # Transformar datos para plotly
        df_melted = df_evolucion.melt(
            id_vars=['Inscripciones'], 
            value_vars=['2020', '2021', '2022', '2023', '2024', '2025'],
            var_name='Año', 
            value_name='Estudiantes'
        )
        df_melted.columns = ['Carrera', 'Año', 'Estudiantes']

        fig = px.line(
            df_melted,
            x='Año',
            y='Estudiantes',
            color='Carrera',
            color_discrete_map=COLORES_CARRERAS,
            markers=True,
            title=f"📈 Evolución Temporal por Carrera ({filtro_tipo})"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Año",
            yaxis_title="Cantidad de Estudiantes"
        )

        return fig
    except Exception as e:
        st.error(f"Error creando gráfico evolución: {e}")
        return None

def crear_grafico_inscripciones_cuatrimestre(df_evolucion):
    """Crea el gráfico de inscripciones por año (columnas apiladas)."""
    try:
        if df_evolucion.empty:
            return None

        # Transformar datos para gráfico apilado
        df_melted = df_evolucion.melt(
            id_vars=['Inscripciones'], 
            value_vars=['2022', '2023', '2024', '2025'],  # Últimos 4 años
            var_name='Año', 
            value_name='Estudiantes'
        )
        df_melted.columns = ['Carrera', 'Año', 'Estudiantes']

        fig = px.bar(
            df_melted,
            x='Año',
            y='Estudiantes',
            color='Carrera',
            color_discrete_map=COLORES_CARRERAS,
            title="📅 Inscripciones 2do Cuatrimestre por Año"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Año",
            yaxis_title="Cantidad de Inscripciones"
        )

        return fig
    except Exception as e:
        st.error(f"Error creando gráfico cuatrimestres: {e}")
        return None

def crear_grafico_cpu_materias(df_cpu):
    """Crea el gráfico de CPU por cantidad de materias."""
    try:
        if df_cpu.empty:
            return None

        fig = px.bar(
            df_cpu,
            x='Inscriptos al CPU',
            y='Inscriptos',
            color_discrete_sequence=[COLORES_CARRERAS['CPU']],
            text='Inscriptos',
            title="📚 CPU: Inscripciones por Cantidad de Materias"
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Cantidad de Materias",
            yaxis_title="Cantidad de Inscriptos"
        )

        return fig
    except Exception as e:
        st.error(f"Error creando gráfico CPU: {e}")
        return None

def main():
    # --- HEADER CON LOGO UNSAM ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo UNSAM (placeholder por ahora)
        st.image("https://via.placeholder.com/300x80/1f77b4/white?text=UNSAM+Logo", width=300)
        st.title("📊 Obsoleto")
        st.markdown("### Inscripciones a Materias - Segundo Cuatrimestre")

    st.markdown("---")

    # --- CARGAR DATOS ---
    kpis = cargar_kpis()
    df_todas = cargar_evolucion_todas()
    df_grado = cargar_evolucion_grado()
    df_cpu_mat = cargar_cpu_materias()

    # --- KPIS SUPERIORES ---
    st.header("📈 Indicadores Clave")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_inscripciones = kpis.get('Total Inscripciones', 0)
        st.metric(
            label="Total Inscripciones",
            value=f"{total_inscripciones:,}".replace(',', '.')
        )

    with col2:
        total_estudiantes = kpis.get('Total Estudiantes', 0)
        st.metric(
            label="Total Estudiantes",
            value=f"{total_estudiantes:,}".replace(',', '.')
        )

    with col3:
        estudiantes_grado = kpis.get('Estudiantes Grado', 0)
        st.metric(
            label="Estudiantes Grado",
            value=f"{estudiantes_grado:,}".replace(',', '.')
        )

    with col4:
        estudiantes_cpu = kpis.get('Estudiantes CPU', 0)
        st.metric(
            label="Estudiantes CPU",
            value=f"{estudiantes_cpu:,}".replace(',', '.')
        )

    st.markdown("---")

    # --- GRÁFICOS CENTRALES ---
    st.header("📊 Visualizaciones")

    # Fila 1: Estudiantes por carrera y Evolución temporal
    col1, col2 = st.columns(2)

    with col1:
        # Toggle para estudiantes por carrera
        filtro_estudiantes = st.radio(
            "Filtrar estudiantes por:",
            ["Todas", "Grado"],
            key="filtro_estudiantes",
            horizontal=True
        )

        df_para_estudiantes = df_grado if filtro_estudiantes == "Grado" else df_todas
        fig1 = crear_grafico_estudiantes_por_carrera(df_para_estudiantes, filtro_estudiantes)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Toggle para evolución temporal
        filtro_evolucion = st.radio(
            "Filtrar evolución por:",
            ["Todas", "Grado"],
            key="filtro_evolucion",
            horizontal=True
        )

        df_para_evolucion = df_grado if filtro_evolucion == "Grado" else df_todas
        fig2 = crear_grafico_evolucion_temporal(df_para_evolucion, filtro_evolucion)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

    # Fila 2: Inscripciones por cuatrimestre y CPU materias
    col3, col4 = st.columns(2)

    with col3:
        fig3 = crear_grafico_inscripciones_cuatrimestre(df_todas)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = crear_grafico_cpu_materias(df_cpu_mat)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

    # --- INFORMACIÓN ADICIONAL ---
    with st.expander("ℹ️ Información sobre los datos"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Carreras incluidas:**")
            st.write("• CP - Contador Público")
            st.write("• LAGE - Lic. en Administración y Gestión de Empresas")
            st.write("• LECO - Lic. en Economía")
            st.write("• LEDC - Lic. en Economía del Desarrollo")
            st.write("• LTUR - Lic. en Turismo")

        with col2:
            st.write("**Otros programas:**")
            st.write("• MPCC - Maestría en Políticas de Ciencia y Tecnología")
            st.write("• GUIA - Guía de Turismo")
            st.write("• CPU - Ciclo de Preparación Universitaria")

        st.write("---")
        st.write("**Período:** Segundo Cuatrimestre 2025")
        st.write("**Última actualización:** ", datetime.now().strftime("%d/%m/%Y %H:%M"))

if __name__ == "__main__":
    main()
