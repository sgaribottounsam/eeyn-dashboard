import dash

# Usamos un "stylesheet" externo para que la app tenga un estilo base
# y para poder usar el sistema de grilla (row, columns).
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Creamos la instancia de la app.
# suppress_callback_exceptions=True es necesario para una app multi-página
# donde los callbacks están definidos en otros archivos.
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

# Esta línea es necesaria para el despliegue en servidores.
server = app.server