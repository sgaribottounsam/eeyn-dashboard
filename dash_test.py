from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

df = pd.read_csv('_output/inscripciones_materias/TODAS_evolucion.csv')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(external_stylesheets=external_stylesheets)

app.layout = dmc.Container([
    dmc.Title('My first TEST', size='h3'),
    
    html.Hr(),
    dmc.RadioGroup(
        [dmc.Radio(i, value=i) for i in range(2020, 2025)],
        id='my-dmc-radio-item',
        value='2025',
        size='sm'
    ),
    dmc.Grid([
        dmc.Col([
            dash_table.DataTable(data=df.to_dict('records'), page_size=12, style_table={'overflowX':'auto'})
        ], span=6),
        dmc.Col([
            dcc.Graph(figure={}, id='graph-placeholder')
        ], span=6)
    ]),
], fluid=True)


@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)

def update_graph(col_chosen):
    fig = px.histogram(df, x='Inscripciones', y=col_chosen, histfunc='avg')
    return fig

if __name__ == '__main__':
    app.run(debug=True)