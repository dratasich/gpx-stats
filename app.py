# %% load
import logging
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine


# %% init logger
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] [%(levelname)s] %(message)s")

# %% database setup
DB = "gpx.db"
logging.info(f"Connect to '{DB}'...")
engine = create_engine(f"sqlite:///{DB}")
TABLE = "summary"
df = pd.read_sql(f"SELECT * from {TABLE}", engine)
df = df.astype({"date": "datetime64"})
logging.info(f"Loaded '{len(df)}' entries from table {TABLE}")
df.info()
print(df.head())

# add columns for grouping
df["year"] = df.apply(lambda row: row.date.year, axis=1)
df["month"] = df.apply(lambda row: row.date.month, axis=1)
df["week"] = df.apply(lambda row: row.date.week, axis=1)

# speed values to standard-running units (km/h)
df["speed (km/h)"] = df["speedMetersPerSecond"] * 3.6
# add pace min/km (from speed in m/s)
df["pace (min/km)"] = 60 / df["speed (km/h)"]

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
                 for x in ['speed (km/h)', 'pace (min/km)']],
        value='speed (km/h)',
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
    fig = px.box(df, x=x, y=y, points="all", color="activity")
    return fig

app.run_server(debug=True)
