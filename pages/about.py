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
                html.Div(
                    [
                        # html.H1("Dangermond Preserve Model Ouput Explorer"),
                        html.Br(),
                        html.H2("Overview"),
                        html.P(
                            "This dashboard serves model output, historic water balance, and station data from instrumented "
                            "groundwater wells in the Dangermond Preserve. The primary use is to visualize model results from CFE, "
                            "a conceptual hydrologic model that offers a Basic Model Interface (BMI) compatible version of the National Water Model. "
                            #
                            "The dashboard serves as an entry point to the data, visualizing monthly aggregations of water balance variables, observations, "
                            "and forcing variables. The full data collection is available at _addlink_, which includes detail and descriptions of the "
                            "output variables, model parameters, calibration steps, and example code for reading output files."
                        ),
                        html.Br(),
                        html.P(
                            [
                                "The source code to run this app is available on github: ",
                                html.A(
                                    "Dangermond Web App Repo",
                                    href="https://your-link-here",
                                    target="_blank",
                                ),
                                ". The repo also contains the code used to generate the monthly aggregations, calculated volumes, and summary statistics.",
                            ]
                        ),
                    ],
                    className="readable-text",
                ),
            ],
        ),
    ]
)
