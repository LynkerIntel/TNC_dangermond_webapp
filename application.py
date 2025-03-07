# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from layouts.header_layout import header_layout

from dash import Dash, html, dcc, Patch, no_update
import plotly.express as px
import dash
import pandas as pd
import json
import time
from datetime import date
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np
from dotenv import load_dotenv
import logging
import sys
import os
import secrets

from flask import session

# serve production ready server
from waitress import serve


def _get_session_id():
    session_key = "session_id"
    if not session.get(session_key):
        session[session_key] = secrets.token_urlsafe(16)
    return session.get(session_key)


def _record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    try:
        record.session_id = _get_session_id()
    except RuntimeError:
        record.session_id = "NO_ACTIVE_SESSION"
    return record


# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Create logger.
logging.basicConfig(format="%(session_id)s - %(message)s")
old_factory = logging.getLogRecordFactory()
logging.setLogRecordFactory(_record_factory)

load_dotenv()


MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
DASH_PROD = os.getenv("DASH_PROD")
print(f"{DASH_PROD=}")


def create_app():
    """
    Create the Flask app.
    """
    server = Flask(__name__)

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )

    log = logging.getLogger(__name__)
    log.info("Creating app")

    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

    # create the Dash app
    application = Dash(
        __name__,
        server=server,
        # suppress_callback_exceptions=True,
        use_pages=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP,
            FONT_AWESOME,
        ],
    )

    # application.layout = dbc.Container(
    #     fluid=True,
    #     id="root",  # most outer container
    #     children=[
    #         header_layout,
    #         dash.page_container,
    #     ],
    #     style={
    #         "padding": "0",
    #         # "width": "100% !important",
    #         "overflow-x": "hidden",
    #     },
    # )

    # Define the app layout
    application.layout = html.Div(
        [
            # Fixed Navbar
            html.Div(
                header_layout,
                style={
                    "position": "fixed",
                    "top": 0,
                    "width": "100%",
                    "z-index": "1000",
                    "background-color": "white",
                },
            ),
            html.Div(
                dash.page_container,
                style={
                    "padding-top": "60px",
                    "max-width": "100%",
                    "overflow-x": "hidden",
                },
            ),
        ]
    )

    # return the Dash app
    return application


if __name__ == "__main__":
    application = create_app()

    if DASH_PROD == "True":
        print("dss is running with production server")
        serve(application.server, host="0.0.0.0", port=10000)
    else:
        print("app is running with development server")
        application.run_server(host="0.0.0.0", debug=True, port=10000)
