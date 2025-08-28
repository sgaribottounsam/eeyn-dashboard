import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    'CP-CCCP-PC': '#5dae8b',     # Contador Público
    'LI-LAGE-P': '#f6f49d',      # Lic. Administración y Gestión Empresarial
    'LI-LECO-P': '#ff7676',      # Lic. en Economía
    'LI-LTUR-P': '#466c95',      # Lic. en Turismo
}

def crear_grafico_duracion_carrera(df):
    """
    Crea un gráfico de barras horizontales de la duración promedio de la carrera.
    """
    try:
        # Renombrar columnas para que sean más legibles en el gráfico
        df.columns = ['Carrera - Plan', 'Cantidad desde 1994', 'Duración promedio', 'Cantidad (2010 en adelante)', 'Duración (2010 en adelante)']
        
        # Reemplazar comas por puntos y convertir a tipo numérico
        df['Duración promedio'] = df['Duración promedio'].str.replace(',', '.').astype(float)
        
        # Ordenar los datos por duración para una mejor visualización
        df = df.sort_values('Duración promedio', ascending=True)

        fig = px.bar(
            df,
            x='Duración promedio',
            y='Carrera - Plan',
            title='Duración Promedio de la Carrera',
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

def main():
    st.header("Análisis de Egresados")
    st.subheader("Duración de la Carrera")

    # Ruta del archivo de datos
    DATA_PATH = '_output/egresados/Egresados_duración.csv'
    
    # Verificar si el archivo existe
    if not os.path.exists(DATA_PATH):
        st.error(f"Error: No se encontró el archivo '{DATA_PATH}'. Asegúrate de que esté en la carpeta correcta.")
        return

    # Cargar los datos
    try:
        df = pd.read_csv(DATA_PATH, encoding='latin1')
    except Exception as e:
        st.error(f"Error al cargar el archivo de egresados: {e}")
        return

    # Mostrar el gráfico
    figura_duracion = crear_grafico_duracion_carrera(df)
    if figura_duracion:
        st.plotly_chart(figura_duracion, use_container_width=True)

if __name__ == "__main__":
    main()