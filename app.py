# %% load
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# %% sample data
df = pd.DataFrame([
        {"date": datetime.strptime("2020-01-05", "%Y-%m-%d"), "speed": 3.1},
        {"date": datetime.strptime("2020-02-05", "%Y-%m-%d"), "speed": 4.0},
        {"date": datetime.strptime("2020-02-09", "%Y-%m-%d"), "speed": 3.5},
        {"date": datetime.strptime("2020-03-05", "%Y-%m-%d"), "speed": 3.3},
        {"date": datetime.strptime("2020-05-05", "%Y-%m-%d"), "speed": 3.0},
    ])

# add columns for grouping
df["year"] = df.apply(lambda row: row.date.year, axis=1)
df["month"] = df.apply(lambda row: row.date.month, axis=1)
df["week"] = df.apply(lambda row: row.date.week, axis=1)

# speed values to standard-running units (km/h)
df["speed"] = df["speed"] * 3.6
# add pace min/km (from speed in m/s)
df["pace"] = 60 / df["speed"]

# %% plot
#fig = px.box(df, x="month", y="speed", points="all")
#fig.show()

# %% ideas
# https://plotly.com/python/2D-Histogram/

# %%
app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("x-axis:"),
    dcc.Checklist(
        id='x-axis',
        options=[{'value': x, 'label': x}
                 for x in ['year', 'month', 'week']],
        value=['month'],
        labelStyle={'display': 'inline-block'}
    ),
    html.P("y-axis:"),
    dcc.RadioItems(
        id='y-axis',
        options=[{'value': x, 'label': x}
                 for x in ['speed', 'pace']],
        value='speed',
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="box-plot"),
])

@app.callback(
    Output("box-plot", "figure"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
)
def box_plot(x, y):
    fig = px.box(df, x=x, y=y, points="all")
    return fig

app.run_server(debug=True)
