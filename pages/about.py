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


layout = html.Div(
    [
        html.Div(
            [
                dcc.Markdown(
                    """

            ## About


            """
                ),
            ],
            style={"padding": "1rem 1rem 1rem 1rem"},
        ),
    ]
)
