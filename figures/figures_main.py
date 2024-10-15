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
