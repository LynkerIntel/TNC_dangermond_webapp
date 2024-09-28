import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.request import urlopen
import json
import data_loader


def mapbox_lines(gdf, gdf_outline, gdf_cat, display_var, ds, gdf_wells):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    # get nexgen output to color polygons by
    colors = ds[display_var].sel(Time="1981-10-01 12:00:00").to_dataframe()
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

    fig.add_trace(
        go.Scattermapbox(
            lat=catchment_lats,
            lon=catchment_lons,
            mode="lines",
            hoverinfo="skip",
            opacity=0,
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
            text=gdf_wells["name"],  # Text labels for each point
            hoverinfo="text",
        )
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
    # print(fig)
    return fig


# def water_balance_fig(dfs):
#     """
#     Define time series figure locations on map.
#     """
#     # subset of full vars
#     model_vars = ["aet", "cwd", "pck", "pet", "rch", "run"]

#     df_all = pd.concat([dfs[i]["fp_1"] for i in model_vars], axis=1)
#     df_all.columns = model_vars

#     fig = px.line(df_all)
#     fig.update_layout(
#         # width=100vh,
#         # height=100vw,
#         autosize=True,
#         margin=dict(l=10, r=10, t=10, b=0),
#         # uirevision="Don't change",
#         # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
#     )
#     fig.update_layout(plot_bgcolor="white")
#     fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
#     fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
#     return fig
