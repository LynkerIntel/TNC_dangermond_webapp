import dash
from dash import html
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
import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np
import os
import boto3
import io


from figures import figures_main
import data_loader
import logging

log = logging.getLogger(__name__)
dash.register_page(__name__, path="/")


MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")


gdf = data_loader.get_local_hydrofabric()
dfs = data_loader.get_s3_cabcm()


fig = figures_main.mapbox_lines(gdf)
wb_fig = figures_main.water_balance_fig(dfs)

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
                                dcc.Graph(
                                    figure=fig,
                                    id="map",
                                    style={"height": "40vh"},
                                    # style={"height": "100vh", "width": "100vw"},
                                    config={"displaylogo": False},
                                    # className="flex-fill",
                                ),
                                dcc.Graph(
                                    figure=wb_fig,
                                    id="map",
                                    # style={"width": "83.1vw", "height": "94vh"},
                                    # style={"height": "100vh", "width": "100vw"},
                                    config={"displaylogo": False},
                                    # className="flex-fill",
                                ),
                            ],
                        ),
                    ),
                    # html.Div(id="coords", style={"display": "none"}),
                    lg=9,
                    # className="col-9",
                    style={
                        "background-color": "white",
                        "padding": "0 0 0 0",
                    },
                ),
                dbc.Col(
                    [
                        html.Div(html.H4("Dangermond Preserve Template")),
                        html.Div(html.P("Dashboard / web app")),
                        html.Hr(
                            style={
                                "borderWidth": "1px",
                                "width": "100%",
                                # "borderColor": "#AB87FF",
                                "opacity": "unset",
                            }
                        ),
                        html.Div("Buttons"),
                        html.Div(
                            [
                                dbc.Button(
                                    "1 Day",
                                    outline=True,
                                    color="secondary",
                                    className="me-1 mb-1",
                                    id="day-button",
                                ),
                                dbc.Button(
                                    "1 Week",
                                    outline=True,
                                    color="secondary",
                                    className="me-1 mb-1",
                                    id="week-button",
                                ),
                                dbc.Button(
                                    "1 Month",
                                    outline=True,
                                    color="secondary",
                                    className="me-1 mb-1",
                                    id="month-button",
                                ),
                                dbc.Button(
                                    "1 Year",
                                    outline=True,
                                    # active = True,
                                    color="secondary",
                                    className="me-1 mb-1",
                                    id="year-button",
                                ),
                            ],
                            className="d-md-flex mt-1",
                        ),
                        html.Div("Or custom range:"),
                        dcc.DatePickerRange(
                            display_format="YYYY/MM/DD",
                            id="date-picker-range",
                            number_of_months_shown=1,
                            month_format="MMM YYYY",
                            end_date_placeholder_text="MMM Do, YY",
                            # start_date=min_df_date, # supplied in callback
                            # end_date=max_df_date, # supplied in callback
                            # min_date_allowed=min_df_date,
                            # max_date_allowed=max_df_date,
                            # start_date_id="button-week",
                            # with_portal=True,
                            style={"zIndex": 1001},
                            className="dash-bootstrap",
                        ),
                        dbc.FormText("(YYYY/MM/DD)"),
                        # html.Div(
                        #     [
                        #         dbc.Button(
                        #             "All Dates",
                        #             outline=True,
                        #             color="primary",
                        #             className="me-1",
                        #         ),
                        #     ]
                        # ),
                        html.Br(),
                        # html.Br(),
                        html.Div(
                            [
                                dbc.Label("Select Button:"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "Button", "value": "Rain"},
                                        {"label": "Button", "value": "Snow"},
                                        {"label": "Button", "value": "Mix"},
                                    ],
                                    value=["Rain", "Snow", "Mix"],
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
                            ],
                            # className="custom-control custom-switch",
                            # style={"padding": "1.5rem 1.5rem 1.5rem 1.5rem"},
                        ),
                        html.Br(),
                        dbc.Label("Select Bounds:"),
                        html.Div(
                            [
                                # html.P("Minimum Elevation"),
                                dbc.Input(
                                    id="input-elev-min",
                                    # debounce=True,
                                    type="number",
                                    # min=0,
                                    # max=5000,
                                    step=1,
                                    placeholder="Minimum",
                                ),
                            ],
                            # id="min-elev",
                            className="mb-2",
                        ),
                        html.Div(
                            [
                                # html.P("Maximum Elevation"),
                                dbc.Input(
                                    # debounce=True,
                                    id="input-elev-max",
                                    type="number",
                                    min=0,
                                    max=5000,
                                    step=1,
                                    placeholder="Maximum",
                                ),
                                dbc.FormText("unit: meters"),
                            ],
                            # id="max-elev",
                        ),
                        html.Br(),
                        html.Hr(
                            style={
                                "borderWidth": "1px",
                                "width": "100%",
                                # "borderColor": "#AB87FF",
                                "opacity": "unset",
                            }
                        ),
                        dbc.Row(
                            [
                                html.H6(
                                    [
                                        "Selections:",
                                        dbc.Badge(
                                            "None",
                                            id="selected-points",
                                            className="ms-1",
                                        ),
                                        # html.Span(
                                        #     "?",
                                        #     id="tooltip-target",
                                        #     style={
                                        #         "textAlign": "center",
                                        #         "color": "white",
                                        #         "padding-top": "2.5px",
                                        #     },
                                        #     className="dot float-right",
                                        # ),
                                        dbc.Tooltip(
                                            "Use the selection tools (Lasso or Box) in the upper right corner to select observations. \
                                                To remove selection: double click outside of the selection area",
                                            target="selected-points",
                                        ),
                                    ]
                                ),
                            ]
                        ),
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
                        html.Br(),
                        html.Div(id="click-modal"),
                        # dash_table.DataTable(df_obs.iloc[0].to_dict()),
                        # html.Div(
                        #     dbc.Table.from_dataframe(
                        #         df_obs.iloc[:1].melt(),
                        #         striped=True,
                        #         bordered=True,
                        #         hover=True,
                        #     ),
                        #     style={"maxHeight": "400px", "overflow": "scroll"},
                        # ),
                        # html.Div(
                        #     <script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.8.1/datepicker.min.js"></script>
                        # ),
                        # html.Div(
                        #     [
                        #         # "DEVELOPMENT FEATURE TESTING",
                        #         dbc.Label("Toggle a bunch"),
                        #         dbc.Checklist(
                        #             options=[
                        #                 {"label": "Option 1", "value": 1},
                        #                 {"label": "Option 2", "value": 2},
                        #                 {
                        #                     "label": "Disabled Option",
                        #                     "value": 3,
                        #                     "disabled": True,
                        #                 },
                        #             ],
                        #             value=[1],
                        #             # id="switches-input",
                        #             switch=True,
                        #         ),
                        #     ],
                        #     className="border rounded",
                        # ),
                    ],
                    # lg=3,
                    className="pt-2",
                    # width=2,
                    # className="mr-1 ml-2 mt-2",
                    # className="mr-1 ml-2 mt-2",
                    # style={
                    #     # "position": "fixed",
                    #     # "display": "inline-block",
                    #     # "height": "100%",
                    #     # "background-color": "white",
                    #     # "padding": "1rem 0rem 0rem 1.5rem",
                    #     "overflow-y": "auto",
                    #     # "height": "800px",
                    #     # "column-gap": "3px",
                    # },
                ),
                # dbc.Col(
                #     # html.Div(dcc.Loading(dcc.Graph(id="cu-swe-timeseries"))),
                #     html.Div(
                #         dcc.Loading(
                #             parent_className="loading_wrapper",
                #             children=[
                #                 dcc.Graph(
                #                     figure=fig,
                #                     id="map",
                #                     # style={"width": "83.1vw", "height": "94vh"},
                #                     style={"height": "93vh"},
                #                     config={"displaylogo": False},
                #                     # className="flex-fill",
                #                 )
                #             ],
                #         ),
                #     ),
                #     # html.Div(id="coords", style={"display": "none"}),
                #     lg=9,
                #     # className="col-9",
                #     style={
                #         "background-color": "white",
                #         "padding": "0 0 0 0",
                #     },
                # ),
            ]
        )
    ]
)


# # Callbacks ----------------
# @callback(
#     Output("map", "figure"),
#     Input("date-picker-range", "start_date"),
#     Input("date-picker-range", "end_date"),
#     Input("switches-input", "value"),
#     Input("input-elev-min", "value"),
#     Input("input-elev-max", "value"),
#     prevent_intial_call=True,
# )
# def update_visualization(start, end, phases, min_elev, max_elev):
#     """
#     Update the map data based on time range and phase selection. This is a
#     partial property callback that only updates data.

#     list 0 is hidden layer to preserve map layout, data traces start at index 1.

#     :param (str) start: start date in "YYYY-MM-DD"
#     :param (str) end: end dat in "YYYY-MM-DD"
#     :param (list) phases: list containing up to three 3 strs of: ["Rain", "Snow", "Mix]

#     :return (go.Patch): Update data for map
#     """
#     log.info("revising map data")
#     print(min_elev, max_elev)

#     df_sub = df_obs[df_obs["datetime_utc"].between(start, end)]
#     df_sub = df_sub[df_sub["phase"].isin(phases)]

#     if min_elev is None:
#         min_elev = 0

#     if max_elev is None:
#         max_elev = 6000

#     df_sub = df_sub[df_sub["elevation.m"].between(min_elev, max_elev)]

#     patched_fig = Patch()

#     # update data and hover info
#     for i, phase in enumerate(["Rain", "Snow", "Mix"]):
#         df = df_sub[df_sub["phase"] == phase]
#         i += 1  # map layer 0 does not contain data traces
#         patched_fig["data"][i]["lat"] = df["map_latitude"]
#         patched_fig["data"][i]["lon"] = df["map_longitude"]

#         # must match "customdata" attribute in figures_main.generate_map()
#         patched_fig["data"][i]["customdata"] = df[
#             [
#                 "elevation.m",
#                 "all.id",
#                 "datetime_utc",
#                 # "local_time",
#             ]
#         ].values

#     return patched_fig


# @callback(
#     Output("download-dataframe-csv", "data"),
#     Input("download-data-button", "n_clicks"),
#     # Input("input-elev-min", "value"),
#     # Input("input-elev-max", "value"),
#     [State("map", "selectedData")],
#     State("date-picker-range", "start_date"),
#     State("date-picker-range", "end_date"),
#     # State("input-elev-min", "value"),
#     # State("input-elev-max", "value"),
#     # State("switches-input", "value"),
#     # State("map", "figure"),
#     prevent_initial_call=True,
#     suppress_callback_exceptions=True,
# )
# def download_prepare(n_clicks, selected_data, start, end):
#     """
#     Subset and save DataFrame to csv. Currently uses "all.id" in processed MROS data
#     to uniquely identify observations.

#     Several columns are dropped, including "all.id" and "map_latitude/map_longitude"
#     as these are the jittered points using for display only.


#     :param (int) n_clicks: unused
#     :param (dict) selectedData: Figure output from plotly.js with selection
#         data, and other state vars
#     :param (str) start: start date in "YYYY-MM-DD"
#     :param (str) end: end dat in "YYYY-MM-DD"

#     :return: Download file from browser.
#     """
#     log.info("download initiated")
#     if selected_data is not None:
#         points = selected_data["points"]
#         log.info("points %s", len(points))

#         if len(points) > 0:
#             ids = [
#                 i["customdata"]
#                 for i in points
#                 if ("customdata" in i) & (i["curveNumber"] != 0)
#             ]
#             # remove any points from trace 0, which is not visible
#             # ids = [i for i in ids if i["curveNumber"] != 0]
#             # using loc based index for now, should be labeled
#             # in future to prevent missing data from causing loc
#             # check to fail
#             ids = [i[2] for i in ids]
#             print(f"{ids=}")

#             # df_sub = df_obs[df_obs["id"].isin(ids)]
#             df_sub = df_obs[df_obs["all.id"].isin(ids)]
#             df_sub = df_sub.drop(columns=["all.id", "map_latitude", "map_longitude"])

#             filename = f"mros_obs_{start}_{end}.csv"

#             log.info("saving file")
#             return dcc.send_data_frame(df_sub.to_csv, filename)

#     log.info("must select points to download")
#     return no_update


# @callback(
#     Output(
#         "map",
#         "figure",
#         allow_duplicate=True,
#     ),
#     Input("map", "relayoutData"),
#     prevent_initial_call=True,
#     suppress_callback_exceptions=True,
# )
# def limit_zoom_level(map_state, traces=4):
#     """
#     Detects map zoom level, and hides points when zoom
#     exceedes a threshold (12.5) A maximum zoom annotation is also
#     displayed.

#     :param (dict) map_state: dict of current map state, from the figure.
#         Updates whenever the zoom level or view coordinates change.
#     :param (int) layers: the number of data traces in the map. This is
#         required in order to turn off visibility and hoverlabels when
#         zoom theshold is exceeded. If this number is set incorrectly,
#         zoom events past the threshold will cause visible errors in
#         the figure.

#     :return (Dash.Patch): partial property update
#     """
#     log.debug(map_state)

#     if len(map_state) > 1:
#         zoom = map_state["mapbox.zoom"]
#         # zoom = fig["layout"]["mapbox"]["zoom"]
#         # print(f"{zoom=}")
#         patched_fig = Patch()

#         if zoom > 12.5:
#             for i in range(1, traces):
#                 patched_fig["data"][i]["marker"]["opacity"] = 0
#                 patched_fig["layout"]["hovermode"] = False
#                 patched_fig["layout"]["annotations"] = [
#                     {
#                         "font": {"color": "black", "size": 18},
#                         "showarrow": False,
#                         "text": "Zoom out to view observations",
#                         "x": 0.5,
#                         "xref": "paper",
#                         "y": 0.5,
#                         "yref": "paper",
#                         "yshift": 10,
#                     }
#                 ]
#         else:
#             for i in range(1, traces):
#                 patched_fig["data"][i]["marker"]["opacity"] = 1
#                 patched_fig["layout"]["hovermode"] = True
#                 del patched_fig["layout"]["annotations"]

#         return patched_fig

#     return no_update


# @callback(
#     Output("selected-points", "children"),
#     Output("download-data-button", "disabled"),
#     [Input("map", "selectedData")],
#     # prevent_initial_call=True,
# )
# def display_selected_data(selected_data):
#     """Show counter with number of selected observations on the nav panel.

#     :param (dict) selectedData: Figure output from plotly.js with selection
#         data, and other state vars
#     :returns (str): number of points.
#     """
#     print(f"{selected_data=}")

#     if selected_data is not None:
#         points = selected_data["points"]
#         if len(points) > 0:
#             return [f"{len(points)}", False]

#     elif selected_data is None:
#         return ["None", True]


# @callback(
#     Output("click-modal", "children"),
#     Output("map", "clickData"),
#     [Input("map", "clickData")],
#     prevent_initial_call=True,
# )
# def display_click_data(clickData):
#     """Get information for select point

#     This callback returns a Modal (pop-up) that displays a datatable showing
#     all available information for selected observation. Currently this
#     includes all fields, but can be subset.

#     :param clickData (dict): click data from map
#     :return (tuple): This is a tuple of the modal div element, and secondly,
#         None. None is used to reset the "clickData" object after the
#         data table is displayed. Without this, if a user clicks on the
#         same point twice, the modal will not open!
#     """
#     if clickData is not None:
#         ob_id = clickData["points"][0]["customdata"][1]
#         print(f"{ob_id=}")

#         # df is melted when called by dbc.Table below
#         res = df_obs[df_obs["all.id"] == ob_id].iloc[:1]
#         res.drop(columns=["map_longitude", "map_latitude"], axis=1, inplace=True)

#         return (
#             html.Div(
#                 [
#                     # dbc.Button("Open modal", id="open", n_clicks=0),
#                     dbc.Modal(
#                         [
#                             dbc.ModalHeader(dbc.ModalTitle("Point Data")),
#                             dbc.ModalBody(
#                                 [
#                                     # html.Div("Point Data:"),
#                                     dbc.Table.from_dataframe(
#                                         res.melt(),
#                                         striped=True,
#                                         bordered=True,
#                                         hover=True,
#                                     ),
#                                 ]
#                             ),
#                             # dbc.ModalFooter(
#                             #     dbc.Button(
#                             #         "Close", id="close", className="ms-auto", n_clicks=0
#                             #     )
#                             # ),
#                         ],
#                         id="modal-body-scroll",
#                         scrollable=True,
#                         is_open=True,
#                     ),
#                 ]
#             ),
#             None,
#         )
#     else:
#         return "Click on the map to get data"


# @callback(
#     [
#         Output("date-picker-range", "start_date"),
#         Output("date-picker-range", "end_date"),
#     ],
#     Input("day-button", "n_clicks"),
#     Input("week-button", "n_clicks"),
#     Input("month-button", "n_clicks"),
#     Input("year-button", "n_clicks"),
#     # prevent_initial_call=True,
# )
# def update_date_picker(day, week, month, year):
#     """
#     Callback to update the date range picker with present values
#     of 1 week, 1 month, and 1 year.

#     :param (str) week: id of week button
#     :param (str) month: id of month button
#     :param (str) year: id of year button
#     :return (list): list with values for start_date and end_date
#         either datetime object of str of YYYY-MM-DD is accepted.
#     """
#     if ctx.triggered_id is None:  # initial condition
#         # set default date interval on app start
#         start_date = dt.today() - timedelta(days=8)

#     if "day-button" == ctx.triggered_id:
#         # print(f"week is {week}")
#         start_date = dt.today() - timedelta(days=1)

#     if "week-button" == ctx.triggered_id:
#         # print(f"week is {week}")
#         start_date = dt.today() - timedelta(days=7)

#     if "month-button" == ctx.triggered_id:
#         # print(f"week is {week}")
#         start_date = dt.today() - timedelta(days=31)

#     if "year-button" == ctx.triggered_id:
#         start_date = dt.today() - timedelta(days=366)

#     return [start_date, dt.today()]
