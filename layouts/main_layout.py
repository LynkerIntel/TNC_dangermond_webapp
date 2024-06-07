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

# This is the NavBar, shown on all pages.

LYNKER_LOGO = "./assets/lynker-logo-white.png"
pages = dash.page_registry.values()
print(pages)

main_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Navbar(
                    dbc.Row(
                        [
                            html.A(
                                # Use row and col to control vertical alignment of logo / brand
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Img(
                                                src=LYNKER_LOGO,
                                                height="37px",
                                                # style={
                                                #     "padding": "0 0 0 0",
                                                #     "margin": "0 0 0 0",
                                                # },
                                            ),
                                            # class_name="mr-0 ml-0 mt-0, mb-0",
                                        ),
                                        dbc.Col(
                                            dbc.Nav(
                                                [
                                                    # dbc.NavItem(
                                                    #     dbc.NavLink(
                                                    #         "About",
                                                    #         # active=True,
                                                    #         href="about",
                                                    #     ),
                                                    # ),
                                                    # dbc.NavItem(
                                                    #     dbc.NavLink(
                                                    #         "User Guide",
                                                    #         href="obs",
                                                    #     )
                                                ]
                                            ),
                                        ),
                                    ],
                                    align="center",
                                    className="g-0",
                                ),
                                href="/",  # link may to home, may need to change in prod
                                style={"textDecoration": "none"},
                            ),
                        ],
                    ),
                    color="#2c3e50",
                    dark=True,
                    # style={"padding": "0 0 0 0"},
                ),
            ],
            # style={"padding": "0 0 0 0"},
        ),
    ],
)
