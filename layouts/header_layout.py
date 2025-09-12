from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc

LYNKER_LOGO = "./assets/lynker-logo-white.png"
TNC_LOGO = "./assets/TNCLogoPrimary_RGB_Rev.png"

header_layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Navbar(
            dbc.Row(
                [
                    # Left-aligned title
                    dbc.Col(
                        html.A(
                            dbc.NavbarBrand(
                                "Dangermond Preserve: NextGen Simulations"
                            ),
                            href="/",
                            style={"textDecoration": "none", "color": "white", "paddingLeft": "20px"},
                        ),
                        width="auto",
                    ),
                    # Navigation Links
                    dbc.Col(
                        dbc.Nav(
                            [
                                dbc.NavLink(
                                    "About",
                                    href="/about",
                                    active="exact",
                                    external_link=False,
                                    className="text-light",
                                ),
                            ],
                            pills=False,
                            className="d-flex",
                        ),
                        width="auto",
                    ),
                    # Right-aligned logo
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    html.Img(
                                        src=TNC_LOGO,
                                        height="37px",
                                        className="me-3",
                                    ),
                                ),
                                html.Div(
                                    html.Img(
                                        src=LYNKER_LOGO,
                                        height="37px",
                                    ),
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                        className="ms-auto d-flex justify-content-end",
                    ),
                ],
                align="center",
                className="w-100",
                justify="start",
            ),
            color="#2c3e50",
            dark=True,
        ),
    ],
    style={
        "position": "sticky",
        "top": 0,
        "z-index": "1000",
        "width": "100%",
    },
)
