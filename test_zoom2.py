import pandas as pd
import plotly.express as px

# int years
df1 = pd.DataFrame({'year': [2020, 2021, 2022], 'val': [10, 20, 30]})
fig1 = px.line(df1, x='year', y='val')
fig1.update_layout(xaxis_range=[2019.5, 2025.5])
print("Int years done")

# string years
df2 = pd.DataFrame({'year': ['2020', '2021', '2022'], 'val': [10, 20, 30]})
fig2 = px.line(df2, x='year', y='val')
fig2.update_layout(xaxis_range=[-0.5, 5.5])
print("String years done")
