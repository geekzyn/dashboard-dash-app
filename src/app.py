import logging
import os
from datetime import date, datetime, timedelta

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from dashboards.models import AzureCosts
from layouts.content import content_layout
from layouts.sidebar import sidebar_layout
from utils.database import Database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
load_dotenv()


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

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
                html.Span("360 DASHBOARD", className="fs-4 d-block text-center"),
            ],
            className="d-flex flex-column align-items-center mb-4 px-3 py-2",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    "AZURE COSTS",
                    href="#",
                    className="mb-2",
                ),
            ],
            vertical=True,
            className="px-3",
        ),
    ],
    className="bg-light sidebar min-vh-100",
)

filters = dbc.Row(
    [
        dbc.Col(
            [
                html.Label("DATE", className="filter-label"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 12, 31),
                    className="date-picker-modern",
                ),
            ],
            width=4,
        ),
        dbc.Col(
            [
                html.Label("ENVIRONMENT", className="filter-label"),
                html.Div(
                    [
                        dbc.Checkbox(
                            id="dev-checkbox",
                            label="DEV",
                            value=False,
                            className="custom-checkbox",
                        ),
                        dbc.Checkbox(
                            id="tst-checkbox",
                            label="TST",
                            value=False,
                            className="custom-checkbox",
                        ),
                        dbc.Checkbox(
                            id="acc-checkbox",
                            label="ACC",
                            value=False,
                            className="custom-checkbox",
                        ),
                        dbc.Checkbox(
                            id="prd-checkbox",
                            label="PRD",
                            value=False,
                            className="custom-checkbox",
                        ),
                    ],
                    className="environment-checkboxes",
                ),
            ],
            width=4,
        ),
        dbc.Col(
            [
                html.Label("APPLICATION", className="filter-label"),
                dbc.Select(
                    id="application-select",
                    options=[{"label": "All", "value": "all"}],
                    value="all",
                    className="modern-select",
                ),
            ],
            width=2,
        ),
        dbc.Col(
            [
                html.Label("CLUSTER", className="filter-label"),
                dbc.Select(
                    id="cluster-select",
                    options=[{"label": "All", "value": "all"}],
                    value="all",
                    className="modern-select",
                ),
            ],
            width=2,
        ),
    ],
    className="g-2 align-items-end",
)


insights_row_top = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H6(
                                    "Total Costs",
                                    className="text-muted",
                                ),
                                html.H2(
                                    "3.1k",
                                    id="azure-total-costs",
                                    className="card-text",
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "height": "100%",
                            },
                        )
                    ],
                ),
                color="light",
                style={"height": "200px"},
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "Total Budget",
                                    className="card-title",
                                    style={"font-size": "1rem"},
                                ),
                                html.P(
                                    id="azure-total-budget",
                                    className="card-text",
                                    style={"font-size": "2rem"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "height": "100%",
                            },
                        )
                    ]
                ),
                color="light",
                inverse=False,
                style={"height": "200px"},
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "Number of Applications",
                                    className="card-title",
                                    style={"font-size": "1rem"},
                                ),
                                html.P(
                                    id="azure-number-apps",
                                    className="card-text",
                                    style={"font-size": "2rem"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                                "alignItems": "center",
                                "height": "100%",
                            },
                        )
                    ]
                ),
                color="light",
                inverse=False,
                style={"height": "200px"},
            ),
            width=4,
        ),
    ],
    style={"marginBottom": "20px", "marginTop": "30px"},
)

content = html.Div(
    [
        html.Div(
            [filters],
            className="p-4",
            style={
                "background": "white",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            },
        ),
        insights_row_top,
        # Add your dashboard content/cards here
    ],
    className="p-4",
    style={"marginLeft": "250px"},
)


# Callbacks to handle toggle behavior for buttons
@app.callback(
    [
        Output("dev-button", "color"),
        Output("tst-button", "color"),
        Output("acc-button", "color"),
        Output("prd-button", "color"),
    ],
    [
        Input("dev-button", "n_clicks"),
        Input("tst-button", "n_clicks"),
        Input("acc-button", "n_clicks"),
        Input("prd-button", "n_clicks"),
    ],
)
def toggle_environment(dev_clicks, tst_clicks, acc_clicks, prd_clicks):
    def toggle_color(clicks):
        return "primary" if clicks and clicks % 2 == 1 else "light"

    return (
        toggle_color(dev_clicks),
        toggle_color(tst_clicks),
        toggle_color(acc_clicks),
        toggle_color(prd_clicks),
    )


app.layout = html.Div([sidebar, content])


if __name__ == "__main__":
    server.run(debug=True)
