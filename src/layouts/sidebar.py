import dash_bootstrap_components as dbc
from dash import html

sidebar_layout = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink("360 DASHBOARD", href="#", active=True, className="mb-3"),
                html.Hr(),
                dbc.NavLink("Azure Costs", href="/azure-costs"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)
