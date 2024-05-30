import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
from urllib.request import urlopen
import json


# def generate_map(MAPBOX_API_KEY, df):
#     """Create map showing data points within the subset dataframe.

#     "id" col is included (but not displayed) in custom data for all,
#     all traces in order to subset selections made for downloads.

#     :param (pd.DataFrame) df: The subset dataframe, reflecting user inputs.
#     :returns (go.Figure) figure with scatter_mapbox map
#     """
#     # Create a trace
#     # px.set_mapbox_access_token(MAPBOX_API_KEY)

#     fig = px.scatter_mapbox(
#         df[:1],
#         lat=df["map_latitude"][:1],
#         lon=df["map_longitude"][:1],
#         # color="green",
#         # color_discrete_sequence=df["color"],
#         zoom=3,
#         center={"lat": 38.5, "lon": -105},
#         opacity=0,
#         mapbox_style="outdoors",
#         # height="100%",
#     )
#     # fig = go.Figure()
#     # fig.update_traces(showlegend=True)

#     fig.add_trace(
#         go.Scattermapbox(
#             # fill = "toself",
#             opacity=0.7,
#             name="Rain",
#             customdata=df[df.phase == "Rain"][
#                 [
#                     "elevation.m",
#                     "all.id",
#                     "datetime_utc",
#                 ]  # TODO piece together a proper timestamp, move customdata list to config file
#             ],
#             mode="markers",
#             # hoverinfo="none",
#             hovertemplate="<br>".join(
#                 [
#                     "<b>Rain</b>",
#                     "Elevation: %{customdata[0]:.0f} m",
#                     "%{customdata[2]|%Y-%m-%d %H:%M} UTC",
#                     "<extra></extra>",
#                 ]
#             ),
#             showlegend=True,
#             lon=df[df.phase == "Rain"]["map_longitude"],
#             lat=df[df.phase == "Rain"]["map_latitude"],
#             line={
#                 "width": 1,
#             },
#             marker={
#                 "size": 7,
#                 "color": "#048A0E",
#             },
#         )
#     )
#     fig.add_trace(
#         go.Scattermapbox(
#             # fill = "toself",
#             opacity=0.7,
#             name="Snow",
#             mode="markers",
#             customdata=df[df.phase == "Snow"][
#                 ["elevation.m", "datetime_utc", "all.id"]
#             ],
#             hovertemplate="<br>".join(
#                 [
#                     "<b>Snow</b>",
#                     "Elevation: %{customdata[0]:.0f} m",
#                     "%{customdata[2]|%Y-%m-%d %H:%M} UTC",
#                     "<extra></extra>",
#                 ]
#             ),
#             # hoverinfo="skip",
#             showlegend=True,
#             lon=df[df.phase == "Snow"]["map_longitude"],
#             lat=df[df.phase == "Snow"]["map_latitude"],
#             marker={
#                 "size": 7,
#                 "color": "#0D52AC",
#             },
#         )
#     )

#     fig.add_trace(
#         go.Scattermapbox(
#             opacity=0.7,
#             name="Mix",
#             mode="markers",
#             # <extra> str removes the auto "name" tag
#             hovertemplate="<br>".join(
#                 [
#                     "<b>Mix</b>",
#                     "Elevation: %{customdata[0]:.0f} m",
#                     "%{customdata[2]|%Y-%m-%d %H:%M} UTC",
#                     "<extra></extra>",
#                 ]
#             ),
#             showlegend=True,
#             customdata=df[df.phase == "Mix"][["elevation.m", "datetime_utc", "all.id"]],
#             lon=df[df.phase == "Mix"]["map_longitude"],
#             lat=df[df.phase == "Mix"]["map_latitude"],
#             line={
#                 "width": 1,
#             },
#             marker={
#                 "size": 7,
#                 "color": "#FFA6C1",
#             },
#         )
#     )

#     # fig.update_layout(
#     #     mapbox_style="outdoors",
#     #     showlegend=True,
#     # )

#     fig.update_layout(
#         # width=100vh,
#         # height=100vw,
#         autosize=True,
#         margin=dict(l=0, r=0, t=0, b=0),
#         uirevision="Don't change",
#         modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
#     )
#     fig.update_layout(
#         legend=dict(
#             x=0.95,
#             y=0.99,
#             xanchor="right",
#             traceorder="normal",
#         ),
#         # modebar={"color": "black", "bgcolor": "rgba(0, 0, 0, 0)"}
#         # hoverlabel={"bgcolor": "black"]},
#         # mapbox_layers=[
#         #     {"below": "traces", "maxzoom": 11},
#         #     {"below": "traces", "maxzoom": 11},
#         # ],
#     )
#     # fig.update_mapboxes(
#     #     patch=[
#     #         {"below": "traces", "maxzoom": 11},
#     #     ]
#     # )

#     fig.update_layout(hoverlabel=dict(font_size=13))

#     # styles = [
#     #     "carto-positron",
#     #     "carto-darkmatter",
#     #     "outdoors",
#     #     "light",
#     #     "open-street-map",
#     # ]

#     # fig.update_layout(
#     #     updatemenus=[
#     #         {
#     #             "buttons": [
#     #                 {
#     #                     "label": s,
#     #                     "method": "relayout",
#     #                     "args": [
#     #                         {
#     #                             "mapbox": {
#     #                                 "style": s,
#     #                                 "center": {"lat": 45.5517, "lon": -73.7073},
#     #                                 "zoom": 9,
#     #                             }
#     #                         }
#     #                     ],
#     #                 }
#     #                 for s in styles
#     #             ],
#     #             "x": 0.01,
#     #             "y": 0.99,
#     #             "pad": {"l": 0},
#     #             "xanchor": "left",
#     #         },
#     #     ],
#     # )

#     # fig.update_layout(
#     #     updatemenus=[
#     #         dict(
#     #             type="buttons",
#     #             direction="down",
#     #             buttons=[
#     #                 dict(
#     #                     label="Mapbox",
#     #                     method="relayout",
#     #                     args=[
#     #                         {
#     #                             "mapbox": {
#     #                                 "style": "carto-darkmatter",
#     #                                 "center": {"lat": 45.5517, "lon": -73.7073},
#     #                                 "zoom": 9,
#     #                             }
#     #                         }
#     #                     ],
#     #                 ),
#     #                 dict(
#     #                     label="Mapbox 2",
#     #                     method="relayout",
#     #                     args=[
#     #                         {
#     #                             "mapbox": {
#     #                                 "style": "outdoors",
#     #                                 "center": {"lat": 45.5517, "lon": -73.7073},
#     #                                 "zoom": 9,
#     #                             }
#     #                         }
#     #                     ],
#     #                 ),
#     #             ],
#     #         )
#     #     ]
#     # )

#     # fig.update_mapboxes(accesstoken=MAPBOX_API_KEY)
#     fig.update_layout(mapbox_accesstoken=MAPBOX_API_KEY)
#     # print(f"style is: {fig['layout']['mapbox_style']}")
#     # print(fig)
#     return fig


def get_choropleth():
    """ """
    with urlopen(
        "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    ) as response:
        counties = json.load(response)

    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
        dtype={"fips": str},
    )

    import plotly.express as px

    fig = px.choropleth(
        df,
        geojson=counties,
        locations="fips",
        color="unemp",
        color_continuous_scale="Viridis",
        range_color=(0, 12),
        scope="usa",
        center={"lon": -120.3, "lat": 34.6},
        # labels={"unemp": "unemployment rate"},
    )
    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(
        # width=100vh,
        # height=100vw,
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        # uirevision="Don't change",
        # modebar={"orientation": "v", "bgcolor": "rgba(255,255,255,1)"},
    )
    fig.update_traces(showlegend=False)
    return fig
