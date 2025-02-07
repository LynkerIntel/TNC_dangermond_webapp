import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.request import urlopen
import shapely.geometry
import numpy as np
import json
import data_loader


def mapbox_lines(
    gdf, gdf_outline, gdf_cat, display_var, ds, gdf_wells, gdf_lines, time
):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    # get nexgen output to color polygons by
    year_month = time[:7]
    print(year_month)
    colors = ds[display_var].sel(Time=year_month).to_dataframe()
    colors = colors[[display_var]]

    gdf_color = pd.merge(gdf, colors, on="catchment", how="outer")

    fig = px.choropleth_mapbox(
        gdf_color,
        geojson=gdf_color.geometry,
        locations=gdf.index,
        opacity=1,
        color=display_var,
        hover_data=["feature_id"],
        center={"lat": 34.51, "lon": -120.47},  # not sure why this is not automatic
        mapbox_style="open-street-map",
        zoom=10.3,
    )

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
    #         customdata=gdf_wells["station_id_dendra"],
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
    # fig.add_trace(
    #     go.Scattermapbox(
    #         lat=gdf_wells["lat"],
    #         lon=gdf_wells["lon"],
    #         mode="markers+text",  # You can also use 'markers' or 'text' alone
    #         marker=go.scattermapbox.Marker(
    #             size=6, color="white"  # You can change the marker color
    #         ),
    #         hovertext=gdf_wells["name"],  # Text labels for each point
    #         customdata=gdf_wells["station_id_dendra"],
    #         # hoverinfo="text",
    #     )
    # )

    fig.update_traces(
        marker_line_width=0, marker_opacity=0, selector=dict(type="choropleth")
    )

    fig.update_layout(
        # width=100vh,
        # height=100vw,
        showlegend=False,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
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
    mean_value = data.terraclim_ann_precip["Annual Precip (mm)"].mean()

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
            "Annual Sum of Groundwater Input/Output",
        ],
    )

    # First plot: Annual Precipitation Bar Chart with Quartile Colors
    fig.add_trace(
        go.Bar(
            x=data.terraclim_ann_precip.index,
            y=data.terraclim_ann_precip["Annual Precip (mm)"],
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
            y=[mean_value] * len(data.terraclim_ann_precip["Annual Precip (mm)"]),
            mode="lines",
            name=f"Mean: {mean_value:.2f}",
            line=dict(color="gray", width=1),
            showlegend=True,
        ),
        row=1,
        col=1,
    )

    # Second plot: Stacked Bar Chart for Groundwater Fluxes
    fig.add_trace(
        go.Bar(
            x=data.gw_delta_yr.index,
            y=data.gw_delta_yr["SOIL_TO_GW_FLUX"],
            name="SOIL_TO_GW_FLUX",
            showlegend=True,
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=data.gw_delta_yr.index,
            y=data.gw_delta_yr["DEEP_GW_TO_CHANNEL"],
            name="DEEP_GW_TO_CHANNEL",
            showlegend=True,
        ),
        row=2,
        col=1,
    )

    # Update layout for stacking in the second plot
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Year"),
        xaxis2=dict(title="Year"),
        yaxis=dict(title="Precipitation (mm)"),
        yaxis2=dict(title="Sum Change (feet)"),
        legend=dict(title="Legend"),
        template="plotly_white",
        height=800,
    )

    return fig


def gw_bar_fig(data):
    """Demo groundwater bar chart fig"""
    # Create the bar chart
    fig = px.bar(
        data.gw_delta_yr["net"],
        title="Annual Change in Groundwater Elevation",
        labels={"index": "Date", "value": "(feet)"},
        template="plotly_white",
    )

    # Center the title
    fig.update_layout(
        title={
            "text": "Annual Change in Groundwater Elevation",  # Title text
            "x": 0.5,  # Centers the title
            "xanchor": "center",  # Anchors the title in the center
        }
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=0, b=10),  # Set bottom margin (b) to 10 pixels
    )
    return fig
