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

import plotly.graph_objects as go

from figures import figures_main
import data_loader
import logging

log = logging.getLogger(__name__)
dash.register_page(__name__, path="/")


MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")


gdf = data_loader.get_local_hydrofabric()
gdf_outline = data_loader.get_outline()
dfs = data_loader.get_s3_cabcm()


map_fig = figures_main.mapbox_lines(gdf, gdf_outline)
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
                                html.Div(html.H4("Dangermond Preserve")),
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
                                # html.Div(id="contents"),
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
                                dcc.DatePickerRange(
                                    display_format="YYYY/MM/DD",
                                    id="date-picker-range",
                                    number_of_months_shown=1,
                                    month_format="MMM YYYY",
                                    end_date_placeholder_text="MMM Do, YY",
                                    style={"zIndex": 1001},
                                    className="dash-bootstrap",
                                ),
                                dbc.FormText("(YYYY/MM/DD)"),
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
                    # className="col-9",
                    style={
                        "background-color": "white",
                        "padding": "0 10 0 0",
                    },
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Graph(
                                figure=map_fig,
                                id="map",
                                style={"height": "40vh"},
                                # style={"height": "100vh", "width": "100vw"},
                                config={"displaylogo": False},
                                # className="flex-fill",
                            ),
                            dcc.Graph(
                                # figure=wb_ts_fig,
                                id="wb_ts_fig",
                                # style={"width": "83.1vw", "height": "94vh"},
                                # style={"height": "100vh", "width": "100vw"},
                                config={"displaylogo": False},
                                # className="flex-fill",
                            ),
                        ]
                    )
                ),
            ],
        )
    ]
)


# # Callbacks ----------------


@callback(Output("contents", "children"), Input("map", "clickData"))
def update_contents(clickData):
    """
    get click data from primary map, add to layout.
    """
    if clickData:
        print("clicked")
        print(clickData)
        fp = clickData["points"][0]["hovertext"]
        # dff = df[df["centroid_lat"] == fips]
    else:
        fp = 1

    return html.Div(
        [
            # dash_table.DataTable(
            #     id="table",
            #     columns=[{"name": i, "id": i} for i in dff.columns],
            #     data=dff.to_dict(orient="records"),
            # )
            fp
        ]
    )


@callback(
    Output("wb_ts_fig", "figure"),
    Input("map", "clickData"),
)
def water_balance_figure(fp_click):
    """
    Define time series figure locations on map.
    """
    if fp_click is None:
        fp = 1
    else:
        fp = fp_click["points"][0]["hovertext"]

    idx = f"fp_{fp}"  # translate number to column
    print(f"{idx=}")
    # subset of full vars
    model_vars = ["aet", "cwd", "pck", "pet", "rch", "run"]
    df_all = pd.concat([dfs[i][idx] for i in model_vars], axis=1)
    df_all.columns = model_vars

    fig = px.line(df_all)
    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=20, r=10, t=45, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )

    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")

    print(fig["data"])
    return fig


@callback(
    Output("map", "figure"),
    Input("map", "clickData"),
    prevent_initial_call=True,
)
def higlight_line_segment_on_map(fp_click):
    """
    Highlight line segment to make user selection more obvious.
    """
    print("highlight callback fired")

    if fp_click is None:
        fp = 1
    else:
        fp = fp_click["points"][0]["hovertext"]

    # country_count = list(df[df.country.isin(countries)].index)
    patched_figure = Patch()
    # updated_markers = ["#ff1397" for i in range(len(dfs["run"]) + 1)]
    # patched_figure["data"][0]["line"]["color"] = updated_markers

    subset = gdf[gdf["ID"] == fp]
    x = list(subset.iloc[0].geometry.coords.xy[0])
    y = list(subset.iloc[0].geometry.coords.xy[1])

    # data[1] is already occupied by the outline trace, so add data[3] as the highlight segment
    patched_figure["data"][2] = go.Scattermapbox(
        mode="lines", lon=x, lat=y, line_color="green", line_width=5, name="test"
    )

    return patched_figure


# @callback(Output("map", "figure"), Input("update_contents", "value"))
# def update_waterbalance_timeseries(click_data):
#     """ """
#     print("updating fig")


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
