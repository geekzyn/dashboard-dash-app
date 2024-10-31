import dash_bootstrap_components as dbc
from dash import html

sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src="/assets/justice.png",
                    height="25%",
                    width="25%",
                    className="d-block mx-auto mb-2",
                ),
                html.Span("360 DASHBOARD", className="fs-4 d-block"),
            ],
            className="d-flex flex-column align-items-center my-4",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "AZURE COSTS",
                    href="#",
                ),
            ],
            vertical=True,
            className="align-items-center",
        ),
    ],
    className="bg-light sidebar min-vh-100",
)
