# Plataforma de Análisis de Datos Académicos - EEYN UNSAM

Este proyecto es una plataforma de análisis y visualización de datos académicos para la Escuela de Economía y Negocios (EEYN) de la Universidad Nacional de San Martín (UNSAM). Consiste en un dashboard web interactivo construido con Dash y Plotly, acompañado de un conjunto de scripts de Python para la limpieza, procesamiento y gestión de una base de datos SQLite.

## Descripción General

El objetivo principal es ofrecer una herramienta intuitiva para explorar y analizar indicadores clave del rendimiento académico, como la evolución de las inscripciones, las tasas de egresados, la distribución de estudiantes y el análisis de cohortes a lo largo del tiempo.

El flujo de datos es el siguiente:
1.  Los datos brutos (generalmente archivos `.xlsx`) se ubican en `data/crudos/`.
2.  Los scripts en `limpiadores/` procesan estos archivos y guardan versiones limpias en `data/procesados/`.
3.  Los scripts en `db_scripts/` toman los datos procesados y los cargan en la base de datos SQLite (`data/base_de_datos/academica.db`).
4.  La aplicación Dash consume los datos directamente desde la base de datos y los archivos procesados para generar las visualizaciones.

## Requisitos Tecnológicos

*   **Lenguaje:** Python 3.8+
*   **Base de Datos:** SQLite
*   **Librerías Principales:**
    *   `pandas`: Para manipulación y análisis de datos.
    *   `dash` y `dash-bootstrap-components`: Para la construcción del dashboard web.
    *   `plotly`: Para la generación de gráficos interactivos.
    *   `SQLAlchemy`: Para la interacción con la base de datos.
    *   `streamlit`: Utilizado para una visualización alternativa.

Todos los requerimientos están listados en el archivo `requirements.txt`.

## Cómo Correr Localmente

Siga estos pasos para poner en funcionamiento la aplicación en su entorno local.

**1. Clonar el Repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd Dashboard
```

**2. (Recomendado) Crear y Activar un Entorno Virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

**3. Instalar Dependencias**
Instale todas las librerías necesarias ejecutando:
```bash
pip install -r requirements.txt
```

**4. Preparación de la Base de Datos**
Para que el dashboard funcione, primero debe procesar los datos y construir la base de datos. Ejecute los scripts en el siguiente orden:

*   **a. Limpieza de datos:**
    Corra los scripts ubicados en la carpeta `limpiadores/`. Por ejemplo:
    ```bash
    python limpiadores/limpiador_inscripciones_carreras.py
    python limpiadores/limpiador_reporte_alumnos.py
    # ... y así sucesivamente con los demás limpiadores.
    ```

*   **b. Creación de la base de datos:**
    Una vez limpios los datos, popule la base de datos ejecutando los scripts de la carpeta `db_scripts/`. Por ejemplo:
    ```bash
    python db_scripts/carreras.py
    python db_scripts/estudiantes.py
    python db_scripts/egresados.py
    # ... y así sucesivamente con los demás scripts.
    ```

**5. Iniciar la Aplicación Principal (Dashboard Dash)**
Una vez que la base de datos está lista, inicie el servidor del dashboard:
```bash
python dash_dashboard/index.py
```
La aplicación estará disponible en su navegador en la dirección: **http://127.0.0.1:8050**

### Visualización Alternativa con Streamlit
El proyecto también contiene una versión más antigua o alternativa del dashboard hecha con Streamlit. Para ejecutarla:
```bash
streamlit run dashboard_eeyn.py
```

## Variables de Entorno

Este proyecto **no requiere** la configuración de ninguna variable de entorno para su funcionamiento básico.
