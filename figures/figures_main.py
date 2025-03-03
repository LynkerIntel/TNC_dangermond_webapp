import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import pandas as pd
from urllib.request import urlopen
import shapely.geometry
import numpy as np
import json
import data_loader


def mapbox_lines(
    gdf,
    gdf_outline,
    gdf_cat,
    display_var,
    ds,
    gdf_wells,
    gdf_lines,
    time,
    cfe_routed_flow_af,
):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    # get nexgen output to color polygons by
    year_month = time[:7]
    print(year_month)

    if display_var == "Q_OUT":
        # if flows, use routed data, not xr.dataset
        colors = cfe_routed_flow_af.loc[year_month]
        colors = colors.melt(var_name="feature_id", value_name="Streamflow Vol. (af)")
        display_var = "Streamflow Vol. (af)"  # set to actual col name in gdf
        gdf_color = pd.merge(gdf, colors, on="feature_id", how="outer")

    else:
        # if any other output vars, just select from xr.dataset
        colors = ds[display_var].sel(Time=year_month).to_dataframe()
        colors = colors[[display_var]]
        gdf_color = pd.merge(gdf, colors, on="catchment", how="outer")

    fig = px.choropleth_mapbox(
        gdf_color,
        geojson=gdf_color.geometry,
        locations=gdf.index,
        opacity=1,
        color=display_var,
        hover_data=["divide_id"],
        center={"lat": 34.51, "lon": -120.47},  # not sure why this is not automatic
        mapbox_style="open-street-map",
        zoom=10.3,
        custom_data=["divide_id"],  # Add your fields
    )

    # Move colorbar title below the colorbar
    # fig.update_layout(
    #     coloraxis_colorbar=dict(
    #         title=dict(text=display_var, side="bottom"),
    #         # y=0.05,
    #     )
    # )

    # add dandgermond outline
    # outline_lats = list(gdf_outline["geometry"][0].exterior.xy[1])
    # outline_lons = list(gdf_outline["geometry"][0].exterior.xy[0])
    # fig.add_trace(
    #     go.Scattermapbox(
    #         lat=outline_lats, lon=outline_lons, mode="lines", hoverinfo="skip"
    #     ),
    # )

    # add catchment outline (single outline currently)
    catchment_lats = list(gdf["geometry"][0].exterior.xy[1])
    catchment_lons = list(gdf["geometry"][0].exterior.xy[0])

    # add flowline
    lats, lons, names = mapbox_line_gdf_fmt(gdf_lines, id_col="divide_id")

    # any additional layers must be added AFTER this layer
    # this is a placeholder for the active polygon highlight
    fig.add_trace(
        go.Scattermapbox(
            lat=catchment_lats,
            lon=catchment_lons,
            mode="lines",
            hoverinfo="skip",
            opacity=0,
        )
    )

    # fig.add_trace(
    #     go.Scattermapbox(
    #         lat=gdf_wells["lat"],
    #         lon=gdf_wells["lon"],
    #         mode="markers+text",  # You can also use 'markers' or 'text' alone
    #         marker=go.scattermapbox.Marker(
    #             size=6, color="white"  # You can change the marker color
    #         ),
    #         hovertext=gdf_wells["name"],  # Text labels for each point
    #         customdata=gdf_wells["station_id_dendra"].to_numpy(),
    #         # hoverinfo="text",
    #     )
    # )

    # add flowlines to map
    fig.add_trace(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode="lines",
            hoverinfo="skip",
            opacity=1,
            line=dict(
                width=1,
                color="black",
            ),
        )
    )

    # Groundwell Location Markers
    fig.add_trace(
        go.Scattermapbox(
            lat=gdf_wells["lat"],
            lon=gdf_wells["lon"],
            mode="markers+text",  # You can also use 'markers' or 'text' alone
            marker=go.scattermapbox.Marker(
                size=6, color="white"  # You can change the marker color
            ),
            hovertext=gdf_wells["name"],  # Text labels for each point
            customdata=gdf_wells["station_id_dendra"],
            # hoverinfo="text",
        )
    )

    fig.update_traces(
        marker_line_width=0, marker_opacity=0, selector=dict(type="choropleth")
    )

    fig.update_layout(
        # width=100vh,
        # height=100vw,
        showlegend=False,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        # paper_bgcolor="#f4f4f4",
        # mapbox={"layerorder": "below"},
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )
    fig.update_layout(
        modebar=dict(
            orientation="v"
        ),  # Move modebar to vertical orientation (left side)
    )
    fig.layout.uirevision = True
    # print(fig)
    return fig


def mapbox_line_gdf_fmt(gdf, id_col="ID"):
    """ """
    lats = []
    lons = []
    names = []

    for feature, name in zip(gdf.geometry, gdf[id_col]):
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name] * len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, None)

    return lats, lons, names


# def precip_bar_fig(data):
#     """Demo bar chart fig"""
#     # Assuming annual_totals is a pandas Series
#     mean_value = data.terraclim_ann_precip.mean()

#     # Create the bar chart
#     fig = px.bar(
#         data.terraclim_ann_precip,
#         title="Annual Precip",
#         labels={"index": "Date", "value": "Mean Rainfall (mm)"},
#         template="plotly_white",
#     )

#     # Add a horizontal line as a separate trace to include it in the legend
#     fig.add_trace(
#         go.Scatter(
#             x=data.terraclim_ann_precip.index,
#             y=[mean_value]
#             * len(data.terraclim_ann_precip),  # Repeat mean_value for the same length
#             mode="lines",
#             name=f"Mean: {mean_value:.2f}",
#             line=dict(color="gray", width=1),
#         )
#     )

#     # Center the title
#     fig.update_layout(
#         title={
#             "text": "Basin Total Precip - TerraClimate",  # Title text
#             "x": 0.5,  # Centers the title
#             "xanchor": "center",  # Anchors the title in the center
#         }
#     )
#     return fig


def precip_bar_fig(data):
    """Demo bar chart fig with an additional stacked bar chart for groundwater fluxes,
    where precipitation bars are colored by quartile.
    """

    # Calculate the mean precipitation value
    mean_value = data.terraclim_ann_precip["wy_precip_inch"].mean()

    quartile_colors = {
        "a far below average": "#E69F00",
        "a below average": "#F4C05D",
        "a near average": "#EDE682",
        "an above average": "#85C0F9",
        "a far above average": "#0072B2",
    }

    # Assign colors based on quartiles
    bar_colors = data.terraclim_ann_precip["Quartile"].map(quartile_colors)

    # Create a subplot with two rows and a shared x-axis
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Basin Total Precipitation (TerraClimate)",
            "Cumulative Change in Ground Water Storage",
        ],
        vertical_spacing=0.15,
    )

    # First plot: Annual Precipitation Bar Chart with Quartile Colors
    fig.add_trace(
        go.Bar(
            x=data.terraclim_ann_precip.index,
            y=data.terraclim_ann_precip["wy_precip_inch"],
            marker=dict(color=bar_colors),
            name="Annual Precipitation",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Add mean precipitation as a horizontal line
    fig.add_trace(
        go.Scatter(
            x=data.terraclim_ann_precip.index,
            y=[mean_value] * len(data.terraclim_ann_precip["wy_precip_inch"]),
            mode="lines",
            name=f"Mean: {mean_value:.2f}",
            line=dict(color="gray", width=1),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Second plot: Stacked Bar Chart for Groundwater Fluxes
    fig.add_trace(
        go.Line(
            x=data.ngen_basinwide_gw_storage.index,
            y=data.ngen_basinwide_gw_storage,
            name="Storage Volume",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # fig.add_trace(
    #     go.Bar(
    #         x=data.gw_delta_yr.index,
    #         y=data.gw_delta_yr["DEEP_GW_TO_CHANNEL"],
    #         name="DEEP_GW_TO_CHANNEL",
    #         showlegend=True,
    #     ),
    #     row=2,
    #     col=1,
    # )

    # Update layout for stacking in the second plot
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Water Year"),
        # xaxis2=dict(title="Year"),
        yaxis=dict(title="Precipitation (inches)"),
        yaxis2=dict(title="(acre-feet)"),
        # legend=dict(title="Legend"),
        template="plotly_white",
        height=800,
        margin=dict(l=50, r=50, t=30, b=40),  # Reduced top/bottom margin
        paper_bgcolor="#f8f8f8",
        plot_bgcolor="#f8f8f8",
    )

    return fig


def plot_q_out(data, cat_id):
    """Plot streamflow for a selected catchment."""
    feature_id = int(cat_id.split("-")[1])  # get int value only
    cfe_flow_series = data.cfe_routed_flow_af[feature_id]

    fig = px.line(cfe_flow_series, title="Streamflow Comparison")

    # fig.add_trace(
    #     go.Scatter(
    #         x=df_ng.index,
    #         y=df_ng.iloc[:, 0],
    #         mode="lines",
    #         name="CFE Streamflow",
    #     )
    # )

    fig.update_layout(
        autosize=True,
        title={"text": f"Catchment - {cat_id}: Streamflow"},
        title_x=0.5,
        yaxis_title="Monthly Volume (acre-feet)",
        uirevision="Don't change",
        plot_bgcolor="white",
        xaxis_title="",
        legend=dict(
            orientation="h",  # Make legend horizontal
            yanchor="top",
            y=-0.2,  # Move below the plot (adjust if needed)
            xanchor="center",
            x=0.5,  # Center the legend
        ),
    )

    return fig


def plot_actual_et(data, cat_id):
    """Plot Actual Evapotranspiration (AET) for a selected catchment."""
    df_aet = data.df_cabcm["aet"]
    df_sub = df_aet[df_aet["divide_id"] == cat_id]

    fig = px.line(df_sub[["value"]])
    fig.update_traces(name="CABCM", showlegend=True)

    df_ng = (
        pd.DataFrame(data.ds_ngen["ACTUAL_ET"].sel({"catchment": cat_id}).to_pandas())
        * 1000  # UNIT: m/month to mm/month
    )

    fig.add_trace(
        go.Scatter(
            x=df_ng.index,
            y=df_ng.iloc[:, 0],
            mode="lines",
            name="CFE AET",
        )
    )

    fig.update_layout(
        yaxis_title="millimeters",
        autosize=True,
        title={"text": f"Catchment - {cat_id}: AET"},
        title_x=0.5,
        uirevision="Don't change",
        plot_bgcolor="white",
        xaxis_title="",
        legend=dict(
            orientation="h",  # Make legend horizontal
            yanchor="top",
            y=-0.2,  # Move below the plot (adjust if needed)
            xanchor="center",
            x=0.5,  # Center the legend
        ),
    )

    return fig


def plot_default(data):
    """Plot default basin streamflow (monthly volume) when no catchment is selected."""
    fig = px.line(data.cfe_q["flow"])
    fig.data[0].name = "CFE Q"  # manually set name

    fig.add_trace(
        go.Scatter(
            x=data.tnc_domain_q.index,
            y=data.tnc_domain_q["monthly_vol_af"],
            mode="lines",
            name="Natural Flows",
        )
    )

    fig.update_layout(
        autosize=True,
        title={"text": f"Basin Streamflow Volume"},
        title_x=0.5,
        yaxis_title="Monthly Volume (acre-feet)",
        uirevision="Don't change",
        plot_bgcolor="white",
        xaxis_title="",
        legend_title_text="",
        # paper_bgcolor="#f4f4f4",
        legend=dict(
            orientation="h",  # Make legend horizontal
            yanchor="top",
            y=-0.2,  # Move below the plot (adjust if needed)
            xanchor="center",
            x=0.5,  # Center the legend
        ),
    )
    # fig.update_xaxes(gridcolor="#f4f4f4")
    # fig.update_yaxes(gridcolor="#f4f4f4")

    return fig


def plot_recharge(data, cat_id):
    """ """


def annual_mean(data):
    """ """
    monthly_mean_by_year = data.ngen_basinwide_input_m3.groupby(
        data.ngen_basinwide_input_m3.index.month
    ).mean()
    monthly_mean_by_year.index = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthly_mean_by_year *= 0.000810714  # UNIT: m^3 to acre-feet

    # mean inflow for all years
    df_input = pd.DataFrame(data.ngen_basinwide_input_m3)
    df_input["water_year"] = df_input.index.map(data.water_year)

    mean_input_all_years = df_input.groupby("water_year").sum().mean()
    mean_input_all_years *= 0.000810714  # UNIT: m^3 to acre-feet

    # mean outflow for all years
    df_et = pd.DataFrame(data.ngen_basinwide_et_loss_m3)
    df_et["water_year"] = df_et.index.map(data.water_year)
    et_wy = df_et.groupby("water_year").sum()

    # get basinwide Q from routed flows attribute
    q_out = data.cfe_q.groupby("water_year").sum()

    mean_et = et_wy["ACTUAL_ET_VOL_M3"].mean() * 0.000810714  # Convert to acre-feet
    mean_q_out = q_out["flow"].mean()

    # make figure
    fig = make_subplots(
        rows=1,
        cols=2,
        # shared_xaxes=True,
        # subplot_titles=[
        #     "Basin Total Precipitation (TerraClimate)",
        #     "Cumulative Change in Ground Water Storage",
        # ],
        subplot_titles=[
            "Mean Basin Inflow Volume by Month",
            "Mean Annual Inflow/Outflow",
        ],
        horizontal_spacing=0.15,
    )
    fig.add_trace(
        go.Bar(
            x=monthly_mean_by_year.index,
            y=monthly_mean_by_year,
            # marker=dict(color=bar_colors),
            name="Annual Inflow Volume (acre-feet)",
            showlegend=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=["Inflow"],
            y=mean_input_all_years,
            # marker=dict(color=bar_colors),
            name="Annual Inflow Volume (acre-feet)",
            marker={"color": "#636efa"},
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    # Add stacked bar for outflows (Q_OUT + ET) under "Outflow"
    fig.add_trace(
        go.Bar(
            x=["Outflow"],
            y=[mean_q_out],
            name="Streamflow (Q_OUT)",
            # marker=dict(color="#636efa"),
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Bar(
            x=["Outflow"],
            y=[mean_et],
            name="Evapotranspiration (ET)",
            # marker=dict(color="#EF553B"),
        ),
        row=1,
        col=2,
    )

    # Update layout to stack bars properly
    fig.update_layout(
        barmode="stack",  # Enable stacking
        yaxis=dict(title="Inflow (acre-feet)"),
        yaxis2=dict(title="Outflow (acre-feet)"),
        plot_bgcolor="white",
    )
    return fig
