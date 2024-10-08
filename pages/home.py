import dash
from dash import html
import datetime
import io
import requests
import dash
from datetime import date as dt, timedelta
import plotly.express as px
import pandas as pd
import time
from datetime import date
from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    callback,
    State,
    Patch,
    no_update,
    dash_table,
    ctx,
)

from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np
import os
import boto3
import io
import xarray as xr

import plotly.graph_objects as go

from figures import figures_main
import data_loader
import logging

log = logging.getLogger(__name__)
dash.register_page(__name__, path="/")


MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")


gdf = data_loader.get_local_hydrofabric(layer="divides")
gdf_outline = data_loader.get_outline()
gdf_cat = data_loader.get_local_hydrofabric(layer="divides")
gdf_wells = data_loader.get_local_hydrofabric(layer="wells")
gdf_lines = data_loader.get_local_hydrofabric(layer="flowpaths")


dfs = data_loader.get_s3_cabcm()
# ds_ngen = data_loader.ngen_csv_to_xr(
#     "/Users/dillonragar/data/tnc/output_2024_09_26/output_24/"
# )

ds_ngen = xr.open_dataset(
    "/Users/dillonragar/data/tnc/ngen_validation_20241008_monthly.nc"
)
df_q = data_loader.ngen_basin_q()
gw_delta = data_loader.monthly_gw_delta(
    "/Users/dillonragar/github/TNC_dangermond/station_data/output/gw_monthly_delta"
)
df_nf = data_loader.natural_flows()

# list of catchments in the ngen output data
cats = ds_ngen["catchment"].to_pandas().to_list()

# fig = px.line(df_q)
fig = go.Figure()

# map_fig = figures_main.mapbox_lines(gdf, gdf_outline, gdf_cat)
# wb_ts_fig = figures_main.water_balance_fig(dfs)


# def layout():
#     """
#     This defines the map layout.
#     """
#     # data is loaded here to initialize the map,
#     # afterwards, all updates are made from a
#     # callback in application.py

#     # df_obs = pd.read_csv("data/mros_met_geog_2023_09_21_noAKCA.csv")
#     # df_obs.index = pd.to_datetime(df_obs["datetime_utc"])

#     # remove leading whitespace from df
#     # df_obs = df_obs.replace(r"^ +| +$", r"", regex=True)

#     fig = figures_main.generate_map(MAPBOX_API_KEY, df_obs)

#     return

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        dcc.Loading(
                            parent_className="loading_wrapper",
                            children=[
                                # html.Div(html.H4("Dangermond Preserve")),
                                html.Div(html.P("Model Output Explorer")),
                                html.Hr(
                                    style={
                                        "borderWidth": "1px",
                                        "width": "100%",
                                        # "borderColor": "#AB87FF",
                                        "opacity": "unset",
                                    }
                                ),
                                html.Br(),
                                # shows selected reach
                                html.Div(id="contents"),
                                #
                                # html.Div("Buttons"),
                                # html.Div(
                                #     [
                                #         dbc.Button(
                                #             "1 Day",
                                #             outline=True,
                                #             color="secondary",
                                #             className="me-1 mb-1",
                                #             id="day-button",
                                #         ),
                                #         dbc.Button(
                                #             "1 Week",
                                #             outline=True,
                                #             color="secondary",
                                #             className="me-1 mb-1",
                                #             id="week-button",
                                #         ),
                                #         dbc.Button(
                                #             "1 Month",
                                #             outline=True,
                                #             color="secondary",
                                #             className="me-1 mb-1",
                                #             id="month-button",
                                #         ),
                                #         dbc.Button(
                                #             "1 Year",
                                #             outline=True,
                                #             # active = True,
                                #             color="secondary",
                                #             className="me-1 mb-1",
                                #             id="year-button",
                                #         ),
                                #     ],
                                #     className="d-md-flex mt-1",
                                # ),
                                html.Div("Select custom time range:"),
                                # dcc.DatePickerSingle(
                                #     display_format="YYYY/MM/DD",
                                #     id="date-picker-range",
                                #     number_of_months_shown=1,
                                #     month_format="MMM YYYY",
                                #     # end_date_placeholder_text="MMM Do, YY",
                                #     style={"zIndex": 1001},
                                #     className="dash-bootstrap",
                                # ),
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": str(year), "value": year}
                                        for year in range(2000, 2031)
                                    ],
                                    value=datetime.datetime.now().year,  # default value is the current year
                                    placeholder="Select a year",
                                ),
                                # Dropdown for selecting month
                                dcc.Dropdown(
                                    id="month-dropdown",
                                    options=[
                                        {"label": "January", "value": 1},
                                        {"label": "February", "value": 2},
                                        {"label": "March", "value": 3},
                                        {"label": "April", "value": 4},
                                        {"label": "May", "value": 5},
                                        {"label": "June", "value": 6},
                                        {"label": "July", "value": 7},
                                        {"label": "August", "value": 8},
                                        {"label": "September", "value": 9},
                                        {"label": "October", "value": 10},
                                        {"label": "November", "value": 11},
                                        {"label": "December", "value": 12},
                                    ],
                                    value=datetime.datetime.now().month,  # default value is the current month
                                    placeholder="Select a month",
                                ),
                                html.Div(id="output-date"),
                                # dbc.FormText("(YYYY/MM/DD)"),
                                html.Br(),
                                # html.Br(),
                                html.Div(
                                    [
                                        dbc.Label("Model Formulation:"),
                                        dbc.Checklist(
                                            options=[
                                                {
                                                    "label": "NextGen",
                                                    "value": "Rain",
                                                },
                                                {
                                                    "label": "LSTM",
                                                    "value": "Snow",
                                                },
                                            ],
                                            value=["Rain", "Snow"],
                                            id="switches-input",
                                            switch=True,
                                            style={
                                                "padding": "0rem 0rem 0rem 1.5rem",
                                                # "color": "pink",
                                            },
                                            # input_style={"color": "pink"},
                                            # input_class_name="custom-checkbox custom-control-input",
                                            # label_checked_class_name="custom-control-label",
                                        ),
                                        dcc.Dropdown(
                                            id="column-dropdown",
                                            options=[
                                                {"label": col, "value": col}
                                                for col in [
                                                    "SOIL_STORAGE",
                                                    "ACTUAL_ET",
                                                    "Q_OUT",
                                                ]
                                            ],
                                            value="Q_OUT",  # Default value
                                        ),
                                    ],
                                    # className="custom-control custom-switch",
                                    # style={"padding": "1.5rem 1.5rem 1.5rem 1.5rem"},
                                ),
                                # html.Br(),
                                # dbc.Label("Select Bounds:"),
                                # html.Div(
                                #     [
                                #         # html.P("Minimum Elevation"),
                                #         dbc.Input(
                                #             id="input-elev-min",
                                #             # debounce=True,
                                #             type="number",
                                #             # min=0,
                                #             # max=5000,
                                #             step=1,
                                #             placeholder="Minimum",
                                #         ),
                                #     ],
                                #     # id="min-elev",
                                #     className="mb-2",
                                # ),
                                # html.Div(
                                #     [
                                #         # html.P("Maximum Elevation"),
                                #         dbc.Input(
                                #             # debounce=True,
                                #             id="input-elev-max",
                                #             type="number",
                                #             min=0,
                                #             max=5000,
                                #             step=1,
                                #             placeholder="Maximum",
                                #         ),
                                #         dbc.FormText("unit: meters"),
                                #     ],
                                #     # id="max-elev",
                                # ),
                                # html.Br(),
                                # html.Hr(
                                #     style={
                                #         "borderWidth": "1px",
                                #         "width": "100%",
                                #         # "borderColor": "#AB87FF",
                                #         "opacity": "unset",
                                #     }
                                # ),
                                # dbc.Row(
                                #     [
                                #         html.H6(
                                #             [
                                #                 "Selections:",
                                #                 dbc.Badge(
                                #                     "None",
                                #                     id="selected-points",
                                #                     className="ms-1",
                                #                 ),
                                #                 dbc.Tooltip(
                                #                     "Use the selection tools (Lasso or Box) in the upper right corner to select observations. \
                                #                 To remove selection: double click outside of the selection area",
                                #                     target="selected-points",
                                #                 ),
                                #             ]
                                #         ),
                                #     ]
                                # ),
                                html.Br(),
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Download Data",
                                            color="primary",
                                            disabled=True,
                                            id="download-data-button",
                                        ),
                                        dcc.Download(id="download-dataframe-csv"),
                                    ],
                                    className="d-grid gap-2",
                                    style={"padding": "1.5rem 0 1.5rem 1.5rem 1.5rem"},
                                ),
                                # html.Br(),
                                # html.Div(id="click-modal"),
                                # dcc.Graph(
                                #     figure=map_fig,
                                #     id="map",
                                #     style={"height": "40vh"},
                                #     # style={"height": "100vh", "width": "100vw"},
                                #     config={"displaylogo": False},
                                #     # className="flex-fill",
                                # ),
                                # dcc.Graph(
                                #     # figure=wb_ts_fig,
                                #     id="wb_ts_fig",
                                #     # style={"width": "83.1vw", "height": "94vh"},
                                #     # style={"height": "100vh", "width": "100vw"},
                                #     config={"displaylogo": False},
                                #     # className="flex-fill",
                                # ),
                            ],
                        ),
                    ),
                    # html.Div(id="coords", style={"display": "none"}),
                    lg=3,
                    className="ml-3 mt-3",
                    # style={
                    #     "background-color": "gray",
                    #     # "padding": "20 20 20 20",
                    #     # "margin": "10 10 10 10",
                    # },
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Graph(
                                # figure=map_fig,
                                id="choropleth-map",
                                style={"height": "40vh"},
                                # style={"height": "100vh", "width": "100vw"},
                                config={"displaylogo": False},
                                # className="flex-fill",
                            ),
                            dcc.Graph(
                                # figure=wb_ts_fig,
                                id="wb_ts_fig",
                                style={"height": "50vh"},
                                # style={"height": "100vh", "width": "100vw"},
                                config={"displaylogo": False},
                                # className="flex-fill",
                            ),
                            # DBC Modal
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(
                                        dbc.ModalTitle(id="well-name-title")
                                    ),
                                    dbc.ModalBody(html.P(id="modal-content")),
                                    dbc.ModalBody(
                                        dcc.Graph(
                                            id="modal-figure",
                                            figure=fig,
                                        )  # Include the figure inside the modal
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button(
                                            "Close",
                                            id="close-modal",
                                            className="ml-auto",
                                            n_clicks=0,
                                        )
                                    ),
                                ],
                                id="modal",
                                size="xl",
                                is_open=False,  # Initially closed
                            ),
                        ]
                    )
                ),
            ],
        )
    ]
)


# # Callbacks ----------------
@callback(Output("contents", "children"), Input("choropleth-map", "clickData"))
def update_contents(click_data):
    """
    get click data from primary map, add to layout.
    """
    if click_data:
        layer = click_data["points"][0]["curveNumber"]
        if layer == 0:
            # print("clicked")
            print(click_data)
            id = click_data["points"][0]["customdata"][0]
            # dff = df[df["centroid_lat"] == fips]
    else:
        id = 1

    return html.Div(
        [
            # dash_table.DataTable(
            #     id="table",
            #     columns=[{"name": i, "id": i} for i in dff.columns],
            #     data=dff.to_dict(orient="records"),
            # )
            id
        ]
    )


# Define the callback to update the output date
@callback(
    Output("output-date", "children"),
    [Input("year-dropdown", "value"), Input("month-dropdown", "value")],
)
def date_from_year_month(year, month):
    if year and month:
        selected_date = datetime.date(year, month, 1).strftime("%Y-%m-%d")
        return f"Selected Date: {selected_date}"
    return "Please select both year and month."


# Callback to update map based on selected column
@callback(Output("choropleth-map", "figure"), [Input("column-dropdown", "value")])
def mapbox_lines(display_var):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    print(display_var)
    return figures_main.mapbox_lines(
        gdf=gdf,
        gdf_outline=gdf_outline,
        gdf_cat=gdf_cat,
        display_var=display_var,
        ds=ds_ngen,
        gdf_wells=gdf_wells,
        gdf_lines=gdf_lines,
    )


# Callback to handle click event and show/hide modal
@callback(
    Output("modal", "is_open"),
    [Input("choropleth-map", "clickData"), Input("close-modal", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(click_data, n_clicks, is_open):
    # check if click_data or None
    if click_data:
        layer = click_data["points"][0]["curveNumber"]

        # set True if well location points have been clicked
        if (layer == 3) and not is_open:
            return True

    # If the close button is clicked, close the modal
    if n_clicks and is_open:
        return False

    return is_open  # Keep modal state unchanged if no click event


# Callback to update modal content based on click_data
@callback(
    Output("well-name-title", "children"),
    Input("choropleth-map", "clickData"),
)
def update_modal_content(click_data):
    if click_data:
        # print(f"{click_data=}")
        layer = click_data["points"][0]["curveNumber"]
        if layer == 3:
            well_name = click_data["points"][0]["hovertext"]
            return f"Groundwater Comparison: {well_name}"
    return ""


# Callback to update modal content based on clickData (optional if dynamic)
@callback(
    Output("modal-figure", "figure"),
    Input("choropleth-map", "clickData"),
    prevent_initial_call=True,
    # suppress_callback_exceptions=True,
)
def update_modal_figure(click_data):
    """Update modal fig

    TODO: subset well locations on plot to only those with good data

    """
    if click_data:
        layer = click_data["points"][0]["curveNumber"]
        if layer == 3:
            print(f"well click: {click_data}")
            # get stn id from click
            stn_id = click_data["points"][0]["customdata"]
            # user stn id to look up catchment
            cat = gdf_wells[gdf_wells["station_id_dendra"] == stn_id][
                "divide_id"
            ].values[0]

            # (1) make sure the stn is within QC-pass set
            if stn_id in gw_delta:
                print("stn id pass")
                # (2) check if cat is valid (model output exists)
                if cat in cats:
                    print("catchment modeled pass")
                    fig = go.Figure()

                    # subset groundwater delta to df
                    df_delta = pd.DataFrame(gw_delta[stn_id].iloc[:, 0])
                    # print(f"{df=}")
                    gw_min_index = df_delta.index.min()
                    gw_max_index = df_delta.index.max()

                    # subset ngen dataset by cat
                    df_ng = (
                        ds_ngen[["DEEP_GW_TO_CHANNEL_FLUX", "SOIL_TO_GW_FLUX"]]
                        .sel({"catchment": cat})
                        .to_pandas()
                    )

                    df_ng = (
                        df_ng[["DEEP_GW_TO_CHANNEL_FLUX", "SOIL_TO_GW_FLUX"]]
                        # .resample("1MS")
                        # .sum()
                        .truncate(before=gw_min_index, after=gw_max_index)
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=df_delta.index,
                            y=df_delta.iloc[:, 0],
                            mode="lines",
                            name="delta distance monthly (meters)",
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=df_ng.index,
                            y=df_ng["SOIL_TO_GW_FLUX"],
                            mode="lines",
                            name="monthly sum (meters)",
                        )
                    )
                    # fig = px.line(df_ng)
                    return fig

    return go.Figure()


@callback(
    Output("wb_ts_fig", "figure"),
    Input("choropleth-map", "clickData"),
)
def water_balance_figure(id_click):
    """
    Define time series figure locations on map.
    """
    # if id_click is None:
    #     id = 2614389
    # else:
    #     id = id_click["points"][0]["customdata"][0]

    # df_sub = df_route[df_route["feature_id"] == id]
    id = id_click["points"][0]["customdata"][0]

    # load natural flows
    df_nf_cat = df_nf[df_nf["divide_id"] == id][["weighted_tnc_flow"]]

    # subset routed NextGen flows

    fig = px.line(df_nf_cat)
    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=20, r=10, t=45, b=0),
        # title={"text": f"Catchment - {id}"},
        title_x=0.5,
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )

    # add model output discharge

    fig.update_layout(plot_bgcolor="white")
    # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
    # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")

    return fig


@callback(
    Output("choropleth-map", "figure", allow_duplicate=True),
    Input("choropleth-map", "clickData"),
    prevent_initial_call=True,
)
def higlight_line_segment_on_map(click_data):
    """
    Highlight line segment to make user selection more obvious. This method use linestrings, rather
    than polygons, to provide higlighting around the polygons.
    """
    if click_data:
        layer = click_data["points"][0]["curveNumber"]

        if layer == 0:
            id = click_data["points"][0]["customdata"][0]
            patched_figure = Patch()

            print(id)
            subset = gdf[gdf["feature_id"] == id]
            print(subset)

            # if geometry is a LINESTRING
            # catchment_lats = list(subset["geometry"][0].exterior.xy[1])
            # catchment_lons = list(subset["geometry"][0].exterior.xy[0])

            # if geometry is a POLYGON
            catchment_lons = list(subset["geometry"].iloc[0].exterior.xy[0])
            catchment_lats = list(subset["geometry"].iloc[0].exterior.xy[1])

            data = go.Scattermapbox(
                lat=catchment_lats,
                lon=catchment_lons,
                mode="lines",
                hoverinfo="skip",
                # line=dict(
                #     width=3,
                #     color="white",
                # ),
                # hovertext=gdf_cat["divide_id"].tolist(),
            )

            patched_figure["data"][1] = data
            return patched_figure

    return no_update
