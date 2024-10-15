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


header_layout = html.Div(
    [
        dbc.Navbar(
            dbc.Row(
                [
                    # Left-aligned title or other content
                    dbc.Col(
                        html.A(
                            dbc.NavbarBrand("Dangermond Preserve: NextGen Simulations"),
                            href="/",
                            style={"textDecoration": "none", "color": "white"},
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.NavItem(
                            dbc.NavLink(
                                "User Guide",
                                href="about",
                            ),
                            style={"color": "gray"},
                        )
                    ),
                    # Empty column to push logo to the right
                    dbc.Col(),
                    # Right-aligned logo
                    dbc.Col(
                        html.Img(
                            src=LYNKER_LOGO,
                            height="37px",
                        ),
                        width="auto",
                        style={"textAlign": "right"},
                    ),
                ],
                align="center",
                justify="between",  # Use justify to spread the items across the navbar
                className="w-100",  # Make sure the row takes the full width of the screen
                # style={"width": "100vw"},
                # no_gutters=True,  # Remove default column gutters
            ),
            color="#2c3e50",
            dark=True,
            # style={
            #     "width": "100vw",
            #     "paddingLeft": "0",
            #     "paddingRight": "0",
            # },  # Ensure full width
        ),
    ],
    # style={
    #     #"padding": "20 20 20 20",
    #     # "margin": "0 0 0 0",
    #     "width": "100vw",
    # },  # Ensure no extra padding/margin on the overall layout
)
