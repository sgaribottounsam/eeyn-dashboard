import pandas as pd
import plotly.express as px

# Prueba con año string (categorical)
df1 = pd.DataFrame({'año': ['2020', '2021', '2022'], 'y': [1,2,3]})
fig1 = px.line(df1, x='año', y='y')
fig1.update_layout(xaxis_range=['2020', '2025'])
fig1.write_html('test_zoom_str.html')

# Prueba con año int (linear)
df2 = pd.DataFrame({'año': [2020, 2021, 2022], 'y': [1,2,3]})
fig2 = px.bar(df2, x='año', y='y')
fig2.update_layout(xaxis_range=['2020', '2025'])
fig2.write_html('test_zoom_int.html')
