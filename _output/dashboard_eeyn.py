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

# Mapa de colores para los planes de estudio
COLORES_PLANES = {
    'Plan nuevo': '#5dae8b',
    'Plan Viejo': '#466c95'
}

# --- Carga de Datos ---
@st.cache_data
def cargar_kpis_inscripciones():
    """Carga los KPIs desde el archivo CSV de inscripciones."""
    try:
        df_kpi = pd.read_csv('_output/inscripciones_materias/KPI_insc_materias.csv', header=None, names=['Indicador', 'Valor'], decimal=',')
        kpis = {row['Indicador']: row['Valor'] for _, row in df_kpi.iterrows()}
        return kpis
    except Exception as e:
        st.error(f"Error cargando KPIs: {e}")
        return {}
    
@st.cache_data
def cargar_kpis_egresados():
    """Carga los KPIs desde el archivo CSV de egresados."""
    try:
        df_kpi = pd.read_csv('_output/egresados/Egresados_KPI.csv', encoding='latin1', header=None, names=['Indicador', 'Valor'], decimal=',')
        kpis = {row['Indicador']: row['Valor'] for _, row in df_kpi.iterrows()}
        print("✅ Archivo Egresados_KPI.csv cargado correctamente.")
        return kpis
    except Exception as e:
        st.error(f"Error cargando KPIs de egresados: {e}")
        return {}

@st.cache_data
def cargar_evolucion_todas():
    """Carga los datos de evolución de todas las carreras."""
    try:
        # Leemos el CSV. Quitamos decimal=',' para manejar la conversión manualmente y de forma más robusta.
        df = pd.read_csv('_output/inscripciones_materias/TODAS_evolucion.csv')
        
        # Columnas que deben ser numéricas
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        
        # Forzamos la conversión a tipo numérico, convirtiendo errores en NaN (Not a Number)
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Reemplazamos los NaN que puedan haber surgido con 0 y convertimos a enteros
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)

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
        # Leemos el CSV. Quitamos decimal=',' para manejar la conversión manualmente y de forma más robusta.
        df = pd.read_csv('_output/inscripciones_materias/GRADO_evolucion.csv')

        # Columnas que deben ser numéricas
        columnas_numericas = ['2020', '2021', '2022', '2023', '2024', '2025']
        
        # Forzamos la conversión a tipo numérico, convirtiendo errores en NaN (Not a Number)
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Reemplazamos los NaN que puedan haber surgido con 0 y convertimos a enteros
        df[columnas_numericas] = df[columnas_numericas].fillna(0).astype(int)

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
        df = pd.read_csv('_output/inscripciones_materias/CPU_cantidad_materias.csv', decimal=',')
        return df
    except Exception as e:
        st.error(f"Error cargando CPU materias: {e}")
        return pd.DataFrame()
        
@st.cache_data
def cargar_datos_egresados():
    """Carga los datos de egresados desde el archivo CSV."""
    try:
        df = pd.read_csv('_output/egresados/Egresados_duración.csv', encoding='latin1', decimal=',')
        df.columns = ['Carrera - Plan', 'Cantidad desde 1994', 'Duración promedio', 'Cantidad (Inscriptos 2009 en adelante)', 'Duración (2009 en adelante)']
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de egresados: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_egresados_2024():
    """Carga los datos de egresados del año 2024."""
    try:
        df = pd.read_csv('_output/egresados/Egresados_2024.csv', encoding='latin1', decimal=',')
        df.columns = ['Carrera', 'Cantidad', 'Duración Promedio']
        df = df[df['Carrera'] != 'Total']
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de egresados 2024: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_egresados_tasa():
    """Carga los datos de tasa de graduación de egresados."""
    try:
        df = pd.read_csv('_output/egresados/Egresados_tasa.csv', encoding='latin1', decimal=',')
        # CORRECCIÓN: Se reemplaza el '%' y luego la coma decimal ',' por un punto '.' antes de convertir a float.
        df['Tasa'] = df['Tasa'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de tasas de egresados: {e}")
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
            color_discrete_sequence=['#8200e1'],
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
        
def crear_grafico_duracion_carrera(df, filtro_duracion='Total'):
    """
    Crea un gráfico de barras horizontales de la duración promedio de la carrera.
    """
    try:
        columna = 'Duración (2009 en adelante)' if filtro_duracion == 'Desde 2009' else 'Duración promedio'
        titulo = f"Duración Promedio de la Carrera ({filtro_duracion})"

        df_plot = df[['Carrera - Plan', columna]].copy()
        df_plot.columns = ['Carrera', 'Duración']
        df_plot = df_plot.sort_values('Duración', ascending=True)

        fig = px.bar(
            df_plot,
            x='Duración',
            y='Carrera',
            title=titulo,
            labels={'Duración': 'Duración promedio en años', 'Carrera': 'Carrera y Plan de Estudios'},
            color='Carrera',
            color_discrete_map=COLORES_CARRERAS,
            text='Duración'
        )

        fig.update_traces(texttemplate='%{text:.1f} años', textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_title="Duración promedio en años",
            yaxis_title="Carrera",
            plot_bgcolor='white',
            showlegend=False
        )

        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de duración de carrera: {e}")
        return None

def crear_grafico_egresados_2024(df):
    """Crea un gráfico de barras para los egresados del año 2024."""
    try:
        df_plot = df.sort_values('Cantidad', ascending=True)

        fig = px.bar(
            df_plot,
            x='Carrera',
            y='Cantidad',
            title='Egresados por Carrera 2024',
            labels={'Cantidad': 'Cantidad de Egresados', 'Carrera': 'Carrera'},
            orientation='v',
            color='Carrera',
            color_discrete_map=COLORES_CARRERAS,
            text='Cantidad'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_title="Carrera",
            yaxis_title="Cantidad de Egresados",
            plot_bgcolor='white',
            showlegend=False
        )
        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de egresados 2024: {e}")
        return None

def crear_grafico_tasa_graduacion(df):
    """Crea un gráfico de columnas para la tasa de graduación."""
    try:
        if df.empty:
            st.warning("Datos de tasas de graduación no disponibles.")
            return None
        
        # Filtrar valores de Tasa iguales a 0
        df_plot = df[df['Tasa'] > 0]
        
        fig = px.bar(
            df_plot,
            x='Carrera',
            y='Tasa',
            color='Plan',
            title='Tasa de graduación',
            labels={'Tasa': 'Tasa de Graduación (%)', 'Carrera': 'Carrera'},
            barmode='group',
            orientation='v',
            color_discrete_map=COLORES_PLANES,
            text='Tasa'
        )
        
        fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%')
        fig.update_layout(
            height=400,
            xaxis_title="Carrera",
            yaxis_title="Tasa de Graduación (%)",
            yaxis_range=[0, df_plot['Tasa'].max() * 1.1],
            plot_bgcolor='white',
            showlegend=True
        )
        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de tasa de graduación: {e}")
        return None
        
def crear_grafico_cantidad_graduados_por_plan(df):
    """Crea un gráfico de barras agrupadas de la cantidad de graduados por plan."""
    try:
        if df.empty:
            st.warning("Datos de graduados por plan no disponibles.")
            return None
        
        # Separar la columna 'Carrera - Plan' en 'Carrera' y 'Plan'
        df[['Carrera', 'Plan']] = df['Carrera - Plan'].str.split(' - ', expand=True)

        fig = px.bar(
            df,
            x='Carrera',
            y='Graduados',
            color='Plan',
            title='Cantidad de graduados por carrera',
            labels={'Graduados': 'Cantidad de Egresados', 'Carrera': 'Carrera'},
            orientation='v',
            color_discrete_map=COLORES_PLANES,
            barmode='group',
            text='Graduados'
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_title="Carrera",
            yaxis_title="Cantidad de Egresados",
            plot_bgcolor='white',
            showlegend=True
        )
        return fig
    except Exception as e:
        st.error(f"Error creando el gráfico de cantidad de graduados por plan: {e}")
        return None

# --- Funciones de Páginas ---

def show_inscripciones_dashboard():
    """Muestra el dashboard de inscripciones a materias."""
    kpis = cargar_kpis_inscripciones()
    df_todas = cargar_evolucion_todas()
    df_grado = cargar_evolucion_grado()
    df_cpu_mat = cargar_cpu_materias()

    st.header("Inscripción a materias")
    st.subheader("Segundo cuatrimestre 2025")

    if kpis:
        kpi_options = list(kpis.keys())
        kpi_options.sort()
        
        if "kpi1_index_insc" not in st.session_state:
            st.session_state.kpi1_index_insc = 0
        if "kpi2_index_insc" not in st.session_state:
            st.session_state.kpi2_index_insc = 1

        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi1_insc"):
                    st.session_state.kpi1_index_insc = (st.session_state.kpi1_index_insc - 1) % len(kpi_options)
            with col_metric:
                st.metric(label=kpi_options[st.session_state.kpi1_index_insc], value=f"{kpis.get(kpi_options[st.session_state.kpi1_index_insc], 0):,}".replace(',', '.'))
            with col_right:
                if st.button("➡️", key="next_kpi1_insc"):
                    st.session_state.kpi1_index_insc = (st.session_state.kpi1_index_insc + 1) % len(kpi_options)

        with col_kpi2:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi2_insc"):
                    st.session_state.kpi2_index_insc = (st.session_state.kpi2_index_insc - 1) % len(kpi_options)
            with col_metric:
                st.metric(label=kpi_options[st.session_state.kpi2_index_insc], value=f"{kpis.get(kpi_options[st.session_state.kpi2_index_insc], 0):,}".replace(',', '.'))
            with col_right:
                if st.button("➡️", key="next_kpi2_insc"):
                    st.session_state.kpi2_index_insc = (st.session_state.kpi2_index_insc + 1) % len(kpi_options)
    else:
        st.error("No se pudieron cargar los datos de los KPIs. Asegúrate de que los archivos estén en la carpeta '_output/inscripciones_materias'.")
    
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        filtro_estudiantes = st.radio("Filtrar estudiantes por:", ["Todas", "Grado"], key="filtro_estudiantes_insc", horizontal=True)
        df_para_estudiantes = df_grado if filtro_estudiantes == "Grado" else df_todas
        fig1 = crear_grafico_estudiantes_por_carrera(df_para_estudiantes, filtro_estudiantes)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        filtro_evolucion = st.radio("Filtrar evolución por:", ["Todas", "Grado"], key="filtro_evolucion_insc", horizontal=True)
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
    st.subheader("Indicadores Clave y Visualizaciones")

    df_egresados = cargar_datos_egresados()
    kpis_egresados_archivo = cargar_kpis_egresados()
    df_egresados_2024 = cargar_egresados_2024()
    df_egresados_tasa = cargar_egresados_tasa()
    
    if not df_egresados.empty and kpis_egresados_archivo:
        kpis_egresados = kpis_egresados_archivo

        kpi_options_egresados = list(kpis_egresados.keys())
        kpi_options_egresados.sort()
        
        if "kpi1_index_egr" not in st.session_state:
            st.session_state.kpi1_index_egr = 0
        if "kpi2_index_egr" not in st.session_state:
            st.session_state.kpi2_index_egr = 1

        col_kpi1, col_kpi2 = st.columns(2)
        with col_kpi1:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi1_egr"):
                    st.session_state.kpi1_index_egr = (st.session_state.kpi1_index_egr - 1) % len(kpi_options_egresados)
            with col_metric:
                kpi_label = kpi_options_egresados[st.session_state.kpi1_index_egr]
                value = kpis_egresados.get(kpi_label, 0)
                st.metric(label=kpi_label, value=value)
            with col_right:
                if st.button("➡️", key="next_kpi1_egr"):
                    st.session_state.kpi1_index_egr = (st.session_state.kpi1_index_egr + 1) % len(kpi_options_egresados)

        with col_kpi2:
            col_left, col_metric, col_right = st.columns([1, 4, 1])
            with col_left:
                if st.button("⬅️", key="prev_kpi2_egr"):
                    st.session_state.kpi2_index_egr = (st.session_state.kpi2_index_egr - 1) % len(kpi_options_egresados)
            with col_metric:
                kpi_label = kpi_options_egresados[st.session_state.kpi2_index_egr]
                value = kpis_egresados.get(kpi_label, 0)
                st.metric(label=kpi_label, value=value)
            with col_right:
                if st.button("➡️", key="next_kpi2_egr"):
                    st.session_state.kpi2_index_egr = (st.session_state.kpi2_index_egr + 1) % len(kpi_options_egresados)

        st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if not df_egresados_2024.empty:
            figura_egresados_2024 = crear_grafico_egresados_2024(df_egresados_2024)
            if figura_egresados_2024:
                st.plotly_chart(figura_egresados_2024, use_container_width=True)
    
    with col2:
        if not df_egresados_tasa.empty:
            figura_cantidad_graduados = crear_grafico_cantidad_graduados_por_plan(df_egresados_tasa)
            if figura_cantidad_graduados:
                st.plotly_chart(figura_cantidad_graduados, use_container_width=True)

    # Segunda fila de gráficos
    col3, col4 = st.columns(2)
    with col3:
        if not df_egresados_tasa.empty:
            figura_tasa = crear_grafico_tasa_graduacion(df_egresados_tasa)
            if figura_tasa:
                st.plotly_chart(figura_tasa, use_container_width=True)
    with col4:
        figura_duracion = crear_grafico_duracion_carrera(df_egresados)
        if figura_duracion:
            st.plotly_chart(figura_duracion, use_container_width=True)
            
    with st.expander("ℹ️ Información sobre los datos"):
        st.write("**Carreras y programas:**")
        st.write("• CP - Contador Público")
        st.write("• LAGE - Lic. en Administración y Gestión Empresarial")
        st.write("• LECO - Lic. en Economía")
        st.write("• LTUR - Lic. en Turismo")
        st.write("• MPCC - Martillero Público y Corredor de Comercio")
        st.write("• GUIA - Tecnicatura Universitaria en Guía Turístico")
        st.write("---")
        st.write("**Período:** Segundo Cuatrimestre 2025")
        st.write("**Última actualización:** ", datetime.now().strftime("%d/%m/%Y %H:%M"))


# --- Función Principal ---
def main():
    st.set_page_config(
        page_title="Dashboard Académico EEyN",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    logo_path = "Logo_eeyn_short.PNG"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)
    else:
        st.sidebar.image("https://via.placeholder.com/200x60/1f77b4/white?text=UNSAM+Logo", width=200)

    with st.sidebar:
        st.title("EEyN - UNSAM")
        st.subheader("Menú")

        if st.button("👨‍🎓 Inscripciones a Materias", key="btn_inscripciones"):
            st.session_state.page = "inscripciones"
        if st.button("🎓 Egresados", key="btn_egresados"):
            st.session_state.page = "egresados"
        
        st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
        st.write("Período: Segundo Cuatrimestre 2025")
        st.write("**Última actualización:** ", datetime.now().strftime("%d/%m/%Y %H:%M"))

    if "page" not in st.session_state:
        st.session_state.page = "inscripciones"
    
    if st.session_state.page == "inscripciones":
        show_inscripciones_dashboard()
    elif st.session_state.page == "egresados":
        show_egresados_dashboard()


if __name__ == "__main__":
    main()
