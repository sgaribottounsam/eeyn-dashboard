import pandas as pd
import plotly.express as px
from dash_dashboard.graph_factory.theme import COMMON_LAYOUT
from dash_dashboard.graph_factory.builders import apply_standard_layout

df = pd.DataFrame({'x': [1,2], 'y': [3,4], 'c': ['A', 'B']})
fig = px.bar(df, x='x', y='y', color='c')
fig = apply_standard_layout(fig)
fig.write_html('test_legend.html')
