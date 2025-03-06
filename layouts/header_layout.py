from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc

LYNKER_LOGO = "./assets/lynker-logo-white.png"

header_layout = html.Div(
    [
        dbc.Navbar(
            dbc.Row(
                [
                    # Left-aligned title
                    dbc.Col(
                        html.A(
                            dbc.NavbarBrand("Dangermond Preserve: NextGen Simulations"),
                            href="/",
                            style={"textDecoration": "none", "color": "white"},
                        ),
                        width="auto",
                    ),
                    # User Guide Link
                    dbc.Col(
                        dbc.NavItem(
                            dbc.NavLink(
                                "User Guide",
                                href="about",
                                className="text-light",
                            )
                        ),
                        width="auto",
                    ),
                    # Right-aligned logo
                    dbc.Col(
                        html.Img(
                            src=LYNKER_LOGO,
                            height="37px",
                        ),
                        width="auto",
                        className="ms-auto",
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
