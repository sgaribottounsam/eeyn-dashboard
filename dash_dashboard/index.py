from dash import dcc, html, Input, Output, State
from datetime import datetime

# Paso 1: Importar la app desde app.py
from app import app
# Importamos el 'server' también, es una buena práctica para el despliegue
from app import server

# Paso 2: Importar los layouts de nuestras páginas.
from pages import inscripciones_materias, egresados, inscripciones_carreras

# --- Estilos Dinámicos ---
# Estilo de la barra lateral cuando está ABIERTA
SIDEBAR_STYLE_OPEN = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#EEEEEE",
    "transition": "all 0.3s ease", # Transición suave
}

# Estilo de la barra lateral cuando está CERRADA
SIDEBAR_STYLE_CLOSED = {
    **SIDEBAR_STYLE_OPEN,
    "left": "-17rem", # La movemos fuera de la pantalla
    "padding": "2rem 0",
}

# Estilo del contenido cuando la barra lateral está ABIERTA
CONTENT_STYLE_OPEN = {
    "marginLeft": "23rem",
    "padding": "2rem 1rem",
    "transition": "all 0.3s ease", # Transición suave
}

# Estilo del contenido cuando la barra lateral está CERRADA
CONTENT_STYLE_CLOSED = {
    **CONTENT_STYLE_OPEN,
    "marginLeft": "6rem",
}

# --- Layout Principal (El esqueleto de la APP) ---
sidebar = html.Div(
    [
        # Eliminamos el logo de aquí
        html.H4("Menú", style={'margin-top':'40px'}),
        dcc.Link('👨‍🎓 Inscripciones a Materias', href='/inscripciones-materias', style={'display': 'block', 'margin': '5px'}),
        dcc.Link('🚀 Inscripciones a Carreras', href='/inscripciones-carreras', style={'display': 'block', 'margin': '5px'}),
        dcc.Link('🎓 Egresados', href='/egresados', style={'display': 'block', 'margin': '5px'}),
        html.Hr(style={'borderColor': 'white'}),
        html.P("Período: Segundo Cuatrimestre 2025", style={'fontSize': '14px'}),
        html.P(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}", style={'fontSize': '14px'})
    ],
    id="sidebar", # Le damos un ID para poder manipularla con el callback
    style=SIDEBAR_STYLE_OPEN, # Estado inicial
)

content = html.Div(
    [
        # Botón para mostrar/ocultar la barra lateral
        html.Button("☰", id="sidebar-toggle", n_clicks=0, style={
            'position': 'fixed',
            'top': '10px',
            'left': '10px',
            'zIndex': 1,
            'padding': '5px 10px',
            'fontSize': '20px',
            'borderWidth': '0px',
            'background': 'transparent',
            'color': '#8200e1'
        }),
        # Añadimos el logo aquí, en la esquina superior derecha
        html.Img(src="https://unsam.edu.ar/img/logo_eeyn.png", style={
            'position': 'fixed',
            'top': '15px',
            'right': '15px',
            'width': '150px',
            'zIndex': 1
        }),
        # Aquí se renderizará el contenido de cada página
        html.Div(id="page-content")
    ],
    id="content-container", # Le damos un ID al contenedor del contenido
    style=CONTENT_STYLE_OPEN # Estado inicial
)


# Asignamos el esqueleto a nuestra aplicación
app.layout = html.Div([
    dcc.Location(id="url"),
    # Componente invisible para almacenar el estado (abierta/cerrada)
    dcc.Store(id='sidebar-state', data={'is_open': True}),
    sidebar,
    content
])


# --- Callback para contraer/expandir la barra lateral ---
@app.callback(
    [Output("sidebar", "style"),
     Output("content-container", "style"),
     Output("sidebar-state", "data")],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar-state", "data")]
)
def toggle_sidebar(n, data):
    # Solo reacciona si el botón fue clickeado
    if n:
        is_open = not data["is_open"]
        if is_open:
            # Si se abre, aplicamos los estilos de "abierta"
            sidebar_style = SIDEBAR_STYLE_OPEN
            content_style = CONTENT_STYLE_OPEN
        else:
            # Si se cierra, aplicamos los estilos de "cerrada"
            sidebar_style = SIDEBAR_STYLE_CLOSED
            content_style = CONTENT_STYLE_CLOSED
        
        # Devolvemos los nuevos estilos y el nuevo estado para guardarlo
        return sidebar_style, content_style, {"is_open": is_open}

    # Estado inicial, no hacer nada hasta el primer clic
    return SIDEBAR_STYLE_OPEN, CONTENT_STYLE_OPEN, data


# --- Callback de Navegación ---
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/egresados':
        return egresados.layout
    elif pathname == '/inscripciones-materias':
        return inscripciones_materias.layout
    else:
        # Por defecto, al entrar a la app ('/') o a '/inscripciones-carreras', se muestra esta página
        return inscripciones_carreras.layout


# --- Punto de Entrada para Ejecutar la App ---
if __name__ == '__main__':
    app.run(debug=True)

