import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    'CP': '#5dae8b',     # Amarillo
    'LAGE': '#f6f49d',   # Azul
    'LECO': '#ff7676',   # Verde
    'LEDC': '#FF8C00',   # Naranja
    'LTUR': '#466c95',   # Rojo
    'MPCC': '#c5705d',   # Celeste
    'GUIA': '#8B4513',   # Marrón
    'CPU': '#8200e1'     # Violeta
}

# --- Carga de Datos ---
@st.cache_data
def cargar_kpis():
    """Carga los KPIs desde el archivo CSV de inscripciones."""
    try:
        # Se modificó la ruta para apuntar a la carpeta _output
        df_kpi = pd.read_csv('_output/inscripciones_materias/KPI_insc_materias.csv', header=None, names=['Indicador', 'Valor'])
        kpis = {row['Indicador']: row['Valor'] for _, row in df_kpi.iterrows()}
        return kpis
    except Exception as e:
        st.error(f"Error cargando KPIs: {e}")
        return {}

@st.cache_data
def cargar_evolucion_todas():
    """Carga los datos de evolución de todas las carreras."""
    try:
        # Se modificó la ruta para apuntar a la carpeta _output
        df = pd.read_csv('_output/inscripciones_materias/TODAS_evolucion.csv')
        df = df.dropna(how='all')
        carreras_df = df[~df['Inscripciones'].str.contains('Total', na=False)]
        return carreras_df
    except Exception as e:
        st.error(f"Error cargando evolución todas: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_evolucion_grado():
    """Carga los datos de evolución solo de carreras de grado."""
    try:
        # Se modificó la ruta para apuntar a la carpeta _output
        df = pd.read_csv('_output/inscripciones_materias/GRADO_evolucion.csv')
        df = df.dropna(how='all')
        carreras_df = df[~df['Inscripciones'].str.contains('Total', na=False)]
        return carreras_df
    except Exception as e:
        st.error(f"Error cargando evolución grado: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_cpu_materias():
    """Carga los datos de CPU por cantidad de materias."""
    try:
        # Se modificó la ruta para apuntar a la carpeta _output
        df = pd.read_csv('_output/inscripciones_materias/CPU_cantidad_materias.csv')
        return df
    except Exception as e:
        st.error(f"Error cargando CPU materias: {e}")
        return pd.DataFrame()
        
@st.cache_data
def cargar_datos_egresados():
    """Carga los datos de egresados desde el archivo CSV."""
    try:
        df = pd.read_csv('_output/egresados/Egresados_duración.csv', encoding='latin1')
        df.columns = ['Carrera - Plan', 'Cantidad desde 1994', 'Duración promedio', 'Cantidad (Inscriptos 2009 en adelante)', 'Duración (2009 en adelante)']
        # Reemplazar comas por puntos y convertir a tipo numérico
        df['Duración promedio'] = df['Duración promedio'].str.replace(',', '.').astype(float)
        df['Duración (2009 en adelante)'] = df['Duración (2009 en adelante)'].str.replace(',', '.').astype(float)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de egresados: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_inscripciones_limpio():
    """Carga el archivo de inscripciones limpias para contar el total de inscriptos."""
    try:
        df = pd.read_csv('_output/inscripciones_limpio.csv')
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de inscripciones: {e}")
        return pd.DataFrame()

# --- Funciones de Gráficos ---

def crear_grafico_estudiantes_por_carrera(df_evolucion, filtro_tipo):
    """Crea el gráfico de estudiantes por carrera para 2025."""
    try:
        if df_evolucion.empty:
            st.warning("Datos de evolución de estudiantes no disponibles.")
            return None
        carreras_2025 = df_evolucion[['Inscripciones', '2025']].copy()
        carreras_2025.columns = ['Carrera', 'Estudiantes']
        carreras_2025 = carreras_2025.sort_values('Estudiantes', ascending=True)
        
        # Filtrar solo carreras con colores definidos
        df_filtered = carreras_2025[carreras_2025['Carrera'].isin(COLORES_CARRERAS.keys())]

        fig = px.bar(
            df_filtered, 
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
            yaxis_title="Carrera",
            plot_bgcolor='white'
        )
        return fig
    except Exception as e:
        st.error(f"Error creando gráfico estudiantes: {e}")
        return None

def crear_grafico_evolucion_temporal(df_evolucion, filtro_tipo):
    """Crea el gráfico de evolución temporal por carrera."""
    try:
        if df_evolucion.empty:
            st.warning("Datos de evolución temporal no disponibles.")
            return None
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
            yaxis_title="Cantidad de Estudiantes",
            plot_bgcolor='white'
        )
        return fig
    except Exception as e:
        st.error(f"Error creando gráfico evolución: {e}")
        return None

def crear_grafico_inscripciones_cuatrimestre(df_evolucion):
    """Crea el gráfico de inscripciones por año (columnas apiladas)."""
    try:
        if df_evolucion.empty:
            st.warning("Datos de inscripciones por cuatrimestre no disponibles.")
            return None
        df_melted = df_evolucion.melt(
            id_vars=['Inscripciones'], 
            value_vars=['2022', '2023', '2024', '2025'],
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
            yaxis_title="Cantidad de Inscripciones",
            plot_bgcolor='white'
        )
        return fig
    except Exception as e:
        st.error(f"Error creando gráfico cuatrimestres: {e}")
        return None

def crear_grafico_cpu_materias(df_cpu):
    """Crea el gráfico de CPU por cantidad de materias."""
    try:
        if df_cpu.empty:
            st.warning("Datos de CPU por materias no disponibles.")
            return None
        fig = px.bar(
            df_cpu,
            x='Inscriptos al CPU',
            y='Inscriptos',
            color_discrete_sequence=['#8200e1'], # Color violeta para CPU
            text='Inscriptos',
            title="📚 CPU: Inscripciones por Cantidad de Materias"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Cantidad de Materias",
            yaxis_title="Cantidad de Inscriptos",
            plot_bgcolor='white'
        )
        return fig
    except Exception as e:
        st.error(f"Error creando gráfico CPU: {e}")
        return None
        
def crear_grafico_duracion_carrera(df):
    """
    Crea un gráfico de barras horizontales de la duración promedio de la carrera.
    """
    try:
        # Ordenar los datos por duración para una mejor visualización
        df = df.sort_values('Duración promedio', ascending=True)

        fig = px.bar(
            df,
            x='Duración promedio',
            y='Carrera - Plan',
            title='Duración Promedio de la Carrera (1994 en adelante)',
            labels={'Duración promedio': 'Duración promedio en años', 'Carrera - Plan': 'Carrera y Plan de Estudios'},
            color='Duración promedio',
            color_continuous_scale='blues',
            text='Duración promedio'
        )

        fig.update_traces(texttemplate='%{text:.1f} años', textposition='outside')
        fig.update_layout(
            height=600,
            xaxis_title="Duración promedio en años",
            yaxis_title="Carrera",
            plot_bgcolor='white',
            showlegend=False
        )

        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de duración de carrera: {e}")
        return None

def crear_grafico_cantidad_egresados(df, filtro):
    """
    Crea un gráfico de barras horizontales de la cantidad de egresados.
    """
    try:
        columna = 'Cantidad (Inscriptos 2009 en adelante)' if filtro == 'Desde 2009' else 'Cantidad desde 1994'
        titulo = f"Cantidad de Egresados ({filtro})"

        # Renombrar columnas y preparar los datos
        df_plot = df[['Carrera - Plan', columna]].copy()
        df_plot.columns = ['Carrera', 'Cantidad']
        df_plot = df_plot.sort_values('Cantidad', ascending=True)
        
        # Filtros de las carreras con el color
        df_plot_filtered = df_plot[df_plot['Carrera'].isin(COLORES_CARRERAS.keys())]

        fig = px.bar(
            df_plot,
            x='Cantidad',
            y='Carrera',
            title=titulo,
            labels={'Cantidad': 'Cantidad de Egresados', 'Carrera': 'Carrera y Plan de Estudios'},
            orientation='h',
            color='Cantidad',
            color_continuous_scale='greens',
            text='Cantidad'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=600,
            xaxis_title="Cantidad de Egresados",
            yaxis_title="Carrera",
            plot_bgcolor='white',
            showlegend=False
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de cantidad de egresados: {e}")
        return None


# --- Funciones de Páginas ---

def show_inscripciones_dashboard():
    """Muestra el dashboard de inscripciones a materias."""
    # --- CARGAR DATOS ---
    kpis = cargar_kpis()
    df_todas = cargar_evolucion_todas()
    df_grado = cargar_evolucion_grado()
    df_cpu_mat = cargar_cpu_materias()

    # --- PANEL CENTRAL ---
    st.header("Inscripción a materias")
    st.subheader("Segundo cuatrimestre 2025")

    # --- KPIS DINÁMICOS CON TOGGLE ---
    if kpis:
        kpi_options = list(kpis.keys())
        kpi_options.sort()
        
        # Inicializar el estado de la sesión
        if "kpi1_index" not in st.session_state:
            st.session_state.kpi1_index = 0
        if "kpi2_index" not in st.session_state:
            st.session_state.kpi2_index = 1

        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi1"):
                    st.session_state.kpi1_index = (st.session_state.kpi1_index - 1) % len(kpi_options)
            with col_metric:
                st.metric(label=kpi_options[st.session_state.kpi1_index], value=f"{kpis.get(kpi_options[st.session_state.kpi1_index], 0):,}".replace(',', '.'))
            with col_right:
                if st.button("➡️", key="next_kpi1"):
                    st.session_state.kpi1_index = (st.session_state.kpi1_index + 1) % len(kpi_options)

        with col_kpi2:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi2"):
                    st.session_state.kpi2_index = (st.session_state.kpi2_index - 1) % len(kpi_options)
            with col_metric:
                st.metric(label=kpi_options[st.session_state.kpi2_index], value=f"{kpis.get(kpi_options[st.session_state.kpi2_index], 0):,}".replace(',', '.'))
            with col_right:
                if st.button("➡️", key="next_kpi2"):
                    st.session_state.kpi2_index = (st.session_state.kpi2_index + 1) % len(kpi_options)
    else:
        st.error("No se pudieron cargar los datos de los KPIs. Asegúrate de que los archivos estén en la carpeta '_output/inscripciones_materias'.")
    
    st.markdown("---")

    # --- GRÁFICOS EN CUADRÍCULA 2x2 ---
    col1, col2 = st.columns(2)
    with col1:
        filtro_estudiantes = st.radio("Filtrar estudiantes por:", ["Todas", "Grado"], key="filtro_estudiantes", horizontal=True)
        df_para_estudiantes = df_grado if filtro_estudiantes == "Grado" else df_todas
        fig1 = crear_grafico_estudiantes_por_carrera(df_para_estudiantes, filtro_estudiantes)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        filtro_evolucion = st.radio("Filtrar evolución por:", ["Todas", "Grado"], key="filtro_evolucion", horizontal=True)
        df_para_evolucion = df_grado if filtro_evolucion == "Grado" else df_todas
        fig2 = crear_grafico_evolucion_temporal(df_para_evolucion, filtro_evolucion)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

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
        st.write("**Carreras y programas:**")
        st.write("• CP - Contador Público")
        st.write("• LAGE - Lic. en Administración y Gestión Empresarial")
        st.write("• LECO - Lic. en Economía")
        st.write("• LEDC - Lic. en Economía del Conocimiento")
        st.write("• LTUR - Lic. en Turismo")
        st.write("• MPCC - Martillero Público y Corredor de Comercio")
        st.write("• GUIA - Tecnicatura Universitaria en Guía Turístico")
        st.write("• CPU - Curso de Preparación Universitaria")
        st.write("---")
        st.write("**Período:** Segundo Cuatrimestre 2025")
        st.write("**Última actualización:** ", datetime.now().strftime("%d/%m/%Y %H:%M"))

def show_egresados_dashboard():
    """Muestra el dashboard de egresados."""
    st.header("Análisis de Egresados")
    st.subheader("Duración y Cantidad de Egresados por Carrera")

    df_egresados = cargar_datos_egresados()
    
    # Mostrar el gráfico de cantidad de egresados
    if not df_egresados.empty:
        st.markdown("---")
        
        filtro_cantidad = st.radio(
            "Filtrar cantidad de egresados por:",
            ["Total", "Desde 2009"],
            key="filtro_cantidad_egresados",
            horizontal=True
        )
        
        figura_cantidad = crear_grafico_cantidad_egresados(df_egresados, filtro_cantidad)
        if figura_cantidad:
            st.plotly_chart(figura_cantidad, use_container_width=True)
    
    # Mostrar el gráfico de duración de carrera
    if not df_egresados.empty:
        st.markdown("---")
        figura_duracion = crear_grafico_duracion_carrera(df_egresados)
        if figura_duracion:
            st.plotly_chart(figura_duracion, use_container_width=True)

# --- Función Principal ---
def main():
    # --- PANEL LATERAL ---
    with st.sidebar:
        st.image("Logo_eeyn_short.PNG", width=200)
        st.title("EEyN - UNSAM")
        st.subheader("Menú")

        if st.button("👨‍🎓 Inscripciones a Materias", key="btn_inscripciones"):
            st.session_state.page = "inscripciones"
        if st.button("🎓 Egresados", key="btn_egresados"):
            st.session_state.page = "egresados"

        st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
        st.write("Período: Segundo Cuatrimestre 2025")
        st.write("Última actualización: ", datetime.now().strftime("%d/%m/%Y %H:%M"))

    # Inicializar el estado de la página si no existe
    if "page" not in st.session_state:
        st.session_state.page = "inscripciones"
    
    # Renderizar la página seleccionada
    if st.session_state.page == "inscripciones":
        show_inscripciones_dashboard()
    elif st.session_state.page == "egresados":
        show_egresados_dashboard()

if __name__ == "__main__":
    main()
