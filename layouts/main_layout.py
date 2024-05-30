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

MROS_LOGO = "./assets/mros_icon.svg"
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
                                        # dbc.Col(
                                        #     html.Img(src=MROS_LOGO, height="37px"),
                                        # ),
                                        # dbc.Col(
                                        #     html.Div(
                                        #         [
                                        #             dbc.NavItem(
                                        #                 [
                                        #                     dbc.NavLink(
                                        #                         "About", href="about"
                                        #                     ),
                                        #                 ],
                                        #                 style={
                                        #                     "padding": "0 1rem 0 1rem"
                                        #                 },
                                        #             ),
                                        #         ],
                                        #     ),
                                        # ),
                                        dbc.Col(
                                            dbc.Nav(
                                                [
                                                    dbc.NavItem(
                                                        dbc.NavLink(
                                                            "About Us",
                                                            # active=True,
                                                            href="about",
                                                        ),
                                                        class_name="mr-4 ml-3",
                                                    ),
                                                    dbc.NavItem(
                                                        dbc.NavLink(
                                                            "User Guide",
                                                            href="obs",
                                                        )
                                                    ),
                                                    # dbc.NavItem(
                                                    #     dbc.NavLink(
                                                    #         "Another link", href="#"
                                                    #     )
                                                    # ),
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
