import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.request import urlopen
import json
import data_loader


def mapbox_lines(gdf, gdf_outline):
    """
    Primary map with flowpaths within Dangermond Preserve.
    """
    # get formatted data
    lats, lons, names = data_loader.mapbox_line_gdf_fmt(gdf)

    fig = px.line_mapbox(
        lat=lats, lon=lons, hover_name=names, mapbox_style="carto-positron", zoom=10
    )

    # add dandgermond outline
    outline_lats = list(gdf_outline["geometry"][0].exterior.xy[1])
    outline_lons = list(gdf_outline["geometry"][0].exterior.xy[0])

    fig.add_trace(go.Scattermapbox(lat=outline_lats, lon=outline_lons, mode="lines"))

    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )
    print(fig)
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
