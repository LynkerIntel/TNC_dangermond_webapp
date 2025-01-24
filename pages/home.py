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


# note, boto3 will ignore this if local aws credentials exist
s3 = boto3.resource(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
)


data = data_loader.DataLoader(s3_resource=s3, bucket_name="tnc-dangermond")


# list of catchments in the ngen output data
cats = data.ds_ngen["catchment"].to_pandas().to_list()
fig = go.Figure()


# map_fig = figures_main.mapbox_lines(gdf, gdf_outline, gdf_cat)
# wb_ts_fig = figures_main.water_balance_fig(dfs)
precip_bar_fig = figures_main.precip_bar_fig(data)
gw_bar_fig = figures_main.gw_bar_fig(data)


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
                                dcc.Store(id="cat-click-store"),
                                # shows selected reach
                                html.Div(id="contents", hidden=True),
                                dbc.Label("Model Formulation:"),
                                dbc.Checklist(
                                    options=[
                                        {
                                            "label": "CFE - Streamflow Cal.",
                                            "value": 1,
                                        },
                                        {
                                            "label": "CFE - Groundwater Cal.",
                                            "value": 2,
                                            "disabled": "True",
                                        },
                                    ],
                                    value=[1],
                                    id="switches-input",
                                    switch=True,
                                    style={
                                        "padding": "0rem 1.5rem 0rem 1.5rem",
                                        # "color": "pink",
                                    },
                                    # input_style={"color": "pink"},
                                    # input_class_name="custom-checkbox custom-control-input",
                                    # label_checked_class_name="custom-control-label",
                                ),
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
                                html.Div("Select year and month:"),
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
                                        for year in range(1983, 2024)
                                    ],
                                    value=2008,  # default value is the current year
                                    placeholder="Select a year",
                                    className="mb-1",
                                    clearable=False,
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
                                    value=1,  # default value is the current month
                                    placeholder="Select a month",
                                    clearable=False,
                                ),
                                # html.Div(id="output-date"),
                                # dbc.FormText("(YYYY/MM/DD)"),
                                # html.Br(),
                                # html.Br(),
                                html.Div(
                                    [
                                        # html.Br(),
                                        dbc.Label("Select Output Variable:"),
                                        dcc.Dropdown(
                                            id="variable-dropdown",
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
                                html.Br(),
                                html.Div("Full Domain Statistics:"),
                                html.Div(
                                    id="comparison-table-container",
                                    children=[
                                        dbc.Table(
                                            html.Tbody(
                                                [
                                                    html.Tr(
                                                        [html.Td("Month"), html.Td("")]
                                                    ),  # Blank cell for month
                                                    html.Tr(
                                                        [
                                                            html.Td(
                                                                "Selected Volume (m³)"
                                                            ),
                                                            html.Td(""),
                                                        ]
                                                    ),  # Blank cell for selected volume
                                                    html.Tr(
                                                        [
                                                            html.Td("Avg Volume (m³)"),
                                                            html.Td(""),
                                                        ]
                                                    ),  # Blank cell for average volume
                                                    html.Tr(
                                                        [
                                                            html.Td("% of Avg"),
                                                            html.Td(""),
                                                        ]
                                                    ),  # Blank cell for % of avg
                                                ]
                                            ),
                                            bordered=True,  # Add table borders
                                            hover=True,  # Enable hover effect
                                            striped=True,  # Stripe the rows
                                            responsive=True,  # Make table responsive
                                            size="sm",  # Small size for a more compact look
                                            style={
                                                "border-radius": "5px",  # Rounded corners
                                                "overflow": "hidden",  # Ensure borders and rounding apply smoothly
                                            },
                                        )
                                    ],
                                ),
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
                                dcc.Store(id="selected-date-store"),
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
                            dcc.Loading(
                                id="loading-spinner-map",
                                delay_show=100,
                                type="default",
                                children=[
                                    dcc.Graph(
                                        id="choropleth-map",
                                        style={"height": "40vh"},
                                        config={
                                            "displaylogo": False,
                                            "scrollZoom": True,
                                        },
                                    ),
                                ],
                            ),
                            dcc.Loading(
                                id="loading-spinner-wb_ts",
                                delay_show=100,
                                type="default",
                                children=[
                                    dcc.Graph(
                                        id="wb_ts_fig",
                                        style={"height": "50vh"},
                                        config={"displaylogo": False},
                                    ),
                                ],
                            ),
                            dcc.Loading(
                                id="loading-spinner-wb_ts",
                                delay_show=100,
                                type="default",
                                children=[
                                    dcc.Graph(
                                        # id="bar_fig"
                                        figure=precip_bar_fig,
                                        style={"height": "50vh"},
                                        config={"displaylogo": False},
                                    ),
                                ],
                            ),
                            # dcc.Loading(
                            #     id="loading-spinner-wb_ts",
                            #     delay_show=100,
                            #     type="default",
                            #     children=[
                            #         dcc.Graph(
                            #             # id="bar_fig"
                            #             figure=gw_bar_fig,
                            #             style={"height": "50vh"},
                            #             config={"displaylogo": False},
                            #         ),
                            #     ],
                            # ),
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
                        ],
                        style={
                            "overflow-y": "scroll",  # Enables vertical scrolling
                            "height": "90vh",  # Sets the height to constrain the content
                        },
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
            # print(click_data)
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
            1
        ]
    )


@callback(
    [
        # Output("output-date", "children"),
        Output("selected-date-store", "data"),
    ],  # Store the selected date
    [Input("year-dropdown", "value"), Input("month-dropdown", "value")],
)
def date_from_year_month(year, month):
    """ """
    if year and month:
        selected_date = datetime.date(year, month, 1).strftime("%Y-%m-%d")
        return [selected_date]
    return None


# Callback to update map based on selected column
@callback(
    Output("choropleth-map", "figure"),
    Input("variable-dropdown", "value"),
    Input("selected-date-store", "data"),
)
def mapbox_lines(display_var, time_click):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    print(display_var)
    print(time_click)
    return figures_main.mapbox_lines(
        gdf=data.gdf,
        gdf_outline=data.gdf_outline,
        gdf_cat=data.gdf,
        display_var=display_var,
        ds=data.ds_ngen,
        gdf_wells=data.gdf_wells,
        gdf_lines=data.gdf_lines,
        time=time_click,
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
        # print(f"{layer=}")
        # print(click_data)
        if layer == 3:
            print(f"well click: {click_data}")
            # get stn id from click
            stn_id = click_data["points"][0]["customdata"]
            print(f"{stn_id=}")
            # user stn id to look up catchment
            cat = data.gdf_wells[data.gdf_wells["station_id_dendra"] == stn_id][
                "divide_id"
            ].values[0]
            print(f"{cat=}")

            # (1) make sure the stn is within QC-pass set
            if stn_id in data.gw_delta:
                print("stn id pass")
                # (2) check if cat is valid (model output exists)
                if cat in cats:
                    print("catchment modeled pass")
                    fig = go.Figure()

                    # subset groundwater delta to df
                    df_delta = pd.DataFrame(data.gw_delta[stn_id].iloc[:, 0])
                    # print(f"{df=}")
                    gw_min_index = df_delta.index.min()
                    gw_max_index = df_delta.index.max()

                    # subset ngen dataset by cat
                    df_ng = (
                        data.ds_ngen[["DEEP_GW_TO_CHANNEL_FLUX", "SOIL_TO_GW_FLUX"]]
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
                            name="Groundwater Distance Change (meters)",
                        )
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=df_ng.index,
                            y=df_ng["SOIL_TO_GW_FLUX"],
                            mode="lines",
                            name="Soil to GW Flux (meters)",
                        )
                    )
                    fig.update_layout(
                        # width=100vh,
                        # height=100vw,
                        # autosize=True,
                        # margin=dict(l=20, r=10, t=45, b=0),
                        title={
                            "text": "Monthly Groundwater Elevation Change & Soil To Groundwater Flux"
                        },
                        title_x=0.5,
                        yaxis_title="Monthly Difference (meters)",
                        # uirevision="Don't change",
                        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
                    )
                    # fig = px.line(df_ng)
                    return fig

    return go.Figure()


@callback(
    Output("wb_ts_fig", "figure"),
    Input("choropleth-map", "clickData"),
    Input("variable-dropdown", "value"),
    State("cat-click-store", "data"),
)
def water_balance_figure(click_data, model_var, stored_cat_click):
    """
    Define time series figure locations on map.
    """
    if click_data:
        layer = click_data["points"][0]["curveNumber"]
        if layer == 0:  # click must be on polyogn layer
            id = click_data["points"][0]["customdata"][0]
            if model_var == "Q_OUT":
                # id = id_click["points"][0]["customdata"][0]
                # print(f"{cat=}")

                # load natural flows
                df_nf_cat = data.df_nf[data.df_nf["divide_id"] == id][
                    ["weighted_tnc_flow"]
                ]

                # subset routed NextGen flows by cat
                df_ng = pd.DataFrame(
                    data.ds_ngen["Q_OUT"].sel({"catchment": f"cat-{id}"}).to_pandas()
                )
                # print(f"{df_ng=}")

                fig = px.line(df_nf_cat, title="test")

                # plot Q_OUT for catchment
                fig.add_trace(
                    go.Scatter(
                        x=df_ng.index,
                        y=df_ng.iloc[:, 0],
                        mode="lines",
                        name="CFE Streamflow",
                    )
                )

                fig.update_layout(
                    # width=100vh,
                    # height=100vw,
                    autosize=True,
                    # margin=dict(l=20, r=10, t=45, b=0),
                    title={"text": f"Catchment - {id}: Streamflow"},
                    title_x=0.5,
                    yaxis_title="m3/s",
                    uirevision="Don't change",
                    # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
                )

                # add model output discharge

                fig.update_layout(plot_bgcolor="white")
                # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
                # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")

                return fig

            if model_var == "ACTUAL_ET":
                # create fig of catchment AET vs. CBACM AET
                print("plotting AET")
                print(f"{stored_cat_click=}")

                # if no basin has been selected previously,
                # use current click callback.
                if not stored_cat_click:
                    stored_cat_click = [id]

                # CABCM
                df_aet = data.df_cabcm["aet"]
                df_sub = df_aet[df_aet["divide_id"] == f"cat-{stored_cat_click[0]}"]
                fig = px.line(df_sub[["value"]])
                fig.update_traces(name="CABCM", showlegend=True)

                # NGEN AET
                df_ng = (
                    pd.DataFrame(
                        data.ds_ngen["ACTUAL_ET"]
                        .sel({"catchment": f"cat-{stored_cat_click[0]}"})
                        .to_pandas()
                    )
                    * 1000  # UNIT: m/month to mm/month
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_ng.index,
                        y=df_ng.iloc[:, 0],  # UNIT
                        mode="lines",
                        name="CFE AET",
                    )
                )
                fig.update_layout(
                    yaxis_title="millimeters",
                    # width=100vh,
                    # height=100vw,
                    autosize=True,
                    # margin=dict(l=20, r=10, t=45, b=0),
                    title={"text": f"Catchment - {id}: AET"},
                    title_x=0.5,
                    uirevision="Don't change",
                    # yaxis_title = "millimeters",
                    # y_label="test",
                    # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
                )

                fig.update_layout(
                    yaxis_title="millimeters",
                )

                return fig

    # if no catchment is selected, timeseries should be full domain
    else:
        # df_nf_domain = df_nf[df_nf["divide_id"] == 50000200160223]
        # fig = px.line(data.df_q)
        fig = px.line(data.cfe_q)

        fig.add_trace(
            go.Scatter(
                x=data.tnc_domain_q.index,
                y=data.tnc_domain_q["monthly_vol_m3"],
                mode="lines",
                name="Natural Flows",
            )
        )
        fig.update_layout(plot_bgcolor="white")
        fig.update_layout(
            # width=100vh,
            # height=100vw,
            autosize=True,
            # margin=dict(l=20, r=10, t=45, b=0),
            title={"text": f"Basin Streamflow (Monthly Volume)"},
            title_x=0.5,
            yaxis_title="Monthly Volume (cubic meters)",
            uirevision="Don't change",
            # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
        )

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

            # print(id)
            subset = data.gdf[data.gdf["feature_id"] == id]
            # print(subset)

            # if geometry is a LINESTRING
            # catchment_lats = list(subset["geometry"][0].exterior.xy[1])
            # catchment_lons = list(subset["geometry"][0].exterior.xy[0])

            # if geometry is a POLYGON
            catchment_lons = list(subset["geometry"].iloc[0].exterior.xy[0])
            catchment_lats = list(subset["geometry"].iloc[0].exterior.xy[1])

            fig_data = go.Scattermapbox(
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

            patched_figure["data"][1] = fig_data
            return patched_figure

    return no_update


@callback(
    Output("cat-click-store", "data"),
    Input("choropleth-map", "clickData"),
)
def store_catchment_click(click_data):
    """ """
    if click_data:
        layer = click_data["points"][0]["curveNumber"]
        print(f"{layer=}")
        if layer == 0:
            cat_id = click_data["points"][0]["customdata"]
            print(cat_id)
            return cat_id


@callback(
    Output("comparison-table-container", "children"),
    Input("selected-date-store", "data"),
)
def update_table(selected_date):
    # Convert the selected date into a pandas datetime object
    selected_date = pd.to_datetime(selected_date)

    # Extract the selected month and year
    selected_month = selected_date.month

    # Filter the DataFrame to get data for the selected month across all years
    # selected_month_df = df_q[df_q.index.month == selected_month]
    selected_month_df = data.tnc_domain_q[
        data.tnc_domain_q.index.month == selected_month
    ]

    # Get the volume for the selected month (for the specific year)
    # selected_month_value = df_q.loc[selected_date, "Simulated Monthly Volume"]
    selected_month_value = data.tnc_domain_q.loc[selected_date, "monthly_vol_m3"]

    # Calculate the average volume for that month across all years
    # average_value = selected_month_df["Simulated Monthly Volume"].mean()
    average_value = selected_month_df["monthly_vol_m3"].mean()

    # Calculate the "% of average" for the selected month
    percent_of_average = (selected_month_value / average_value) * 100

    # Format the data for display
    formatted_selected_value = f"{selected_month_value:,.0f}"
    formatted_average_value = f"{average_value:,.0f}"
    formatted_percent_of_average = f"{percent_of_average:.0f}%"

    # Construct the dbc.Table with a vertical layout
    table = dbc.Table(
        # Table header
        [
            # Table body with data in vertical layout
            html.Tbody(
                [
                    html.Tr(
                        [html.Td("Month"), html.Td(selected_date.strftime("%B %Y"))]
                    ),  # Month Year
                    html.Tr(
                        [
                            html.Td("Monthly Volume (m³)"),
                            html.Td(formatted_selected_value),
                        ]
                    ),  # Selected month value
                    html.Tr(
                        [html.Td("Avg Volume (m³)"), html.Td(formatted_average_value)]
                    ),  # Average value for month
                    html.Tr(
                        [html.Td("% of Avg"), html.Td(formatted_percent_of_average)]
                    ),  # % of average
                ]
            )
        ],
        bordered=True,  # Add table borders
        hover=True,  # Enable hover effect
        striped=True,  # Stripe the rows
        responsive=True,  # Make table responsive
        size="sm",  # Small size for a more compact look
        style={
            "border-radius": "5px",  # Rounded corners
            "overflow": "hidden",  # Ensure borders and rounding apply smoothly
        },
    )

    return table


def describe_conditions():
    """
    Create a summary description of climatic conditions for a given year-month condition.
    """
