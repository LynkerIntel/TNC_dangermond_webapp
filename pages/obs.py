import dash
from dash import html
import dash
from dash import html
from dash import Dash, html, dcc
import dash
import plotly.express as px
import pandas as pd
import time
from datetime import date
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np


dash.register_page(__name__)

df = pd.read_csv("./data/mros_met_geog_metadata.csv")

layout = dbc.Col(
    [
        html.Div(
            [
                dcc.Markdown(
                    """
            ## Where do these observations come from?

            The data presented on the map is collected by volunteer observers, for the [Mountain Rain or Snow](https://www.rainorsnow.org/home) project.
        

            ## How do I download data?
            *screenshots*

            ## What are the other variables associated with each observation?

            The following table provides a description of the variables associated with each precipitation phase observation. 
            These variables are returned for all observations and can be accessed by downloading selections on the web map, 
            or by clicking points in the web map to access individual observations.
            """
                ),
            ],
            # style={"padding": "1rem 1rem 1rem 1rem"},
        ),
        html.Div(
            [
                dbc.Table.from_dataframe(
                    df,
                    striped=True,
                    bordered=True,
                    hover=True,
                )
            ],
            className="mr-4",
        ),
    ],
    class_name="m-4",
)
