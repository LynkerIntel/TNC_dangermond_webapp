import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.request import urlopen
import json
import data_loader

# def get_choropleth():
#     """ """
#     with urlopen(
#         "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
#     ) as response:
#         counties = json.load(response)

#     df = pd.read_csv(
#         "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#         dtype={"fips": str},
#     )

#     import plotly.express as px

#     fig = px.choropleth(
#         df,
#         geojson=counties,
#         locations="fips",
#         color="unemp",
#         color_continuous_scale="Viridis",
#         range_color=(0, 12),
#         scope="usa",
#         center={"lon": -120.3, "lat": 34.6},
#         # labels={"unemp": "unemployment rate"},
#     )
#     # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
#     fig.update_layout(
#         # width=100vh,
#         # height=100vw,
#         autosize=True,
#         margin=dict(l=0, r=0, t=0, b=0),
#         # uirevision="Don't change",
#         # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
#     )
#     fig.update_traces(showlegend=False)
#     return fig


def mapbox_lines(gdf):
    """ """
    lats, lons, names = data_loader.mapbox_line_gdf_fmt(gdf)
    fig = px.line_mapbox(
        lat=lats, lon=lons, hover_name=names, mapbox_style="carto-positron"
    )
    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )
    return fig


def water_balance_fig(dfs):
    """ """
    fig = px.line(dfs["run"]["fp_1"])
    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )
    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#f7f7f7")
    return fig
