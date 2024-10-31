import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from dashboards.models import AzureCosts
from layouts.sidebar import sidebar
from utils.database import Database

azure_costs_filters = dbc.Row(
    [
        dbc.Col(
            [
                html.Label("DATE", className="filter-label"),
                dcc.DatePickerRange(
                    id="azure-costs-date-range",
                    start_date=min_date,
                    end_date=max_date,
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
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
                            id=f"azure-costs-{env}-checkbox",
                            label=env.upper(),
                            value=True,
                            className="custom-checkbox",
                        )
                        for env in unique_envs
                    ],
                    className="environment-checkboxes",
                ),
            ],
            width=4,
        ),
        dbc.Col(
            [
                html.Label("APPLICATION", className="filter-label"),
                dcc.Dropdown(
                    id="azure-costs-application-select",
                    options=[{"label": app, "value": app} for app in unique_apps],
                    value=[],
                    multi=True,
                    placeholder="Select applications",
                    className="modern-dropdown",
                ),
            ],
            width=2,
        ),
        dbc.Col(
            [
                html.Label("CLUSTER", className="filter-label"),
                dcc.Dropdown(
                    id="azure-costs-cluster-select",
                    options=[
                        {"label": cluster, "value": cluster}
                        for cluster in unique_clusters
                    ],
                    value=[],
                    multi=True,
                    placeholder="Select clusters",
                    className="modern-dropdown",
                ),
            ],
            width=2,
        ),
    ],
    className="g-2 align-items-end",
)

metrics_row_top = dbc.Row(
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
                                    "€0.00",
                                    id="azure-costs-total-costs",
                                    className="card-text",
                                ),
                            ],
                            className="d-flex flex-column justify-content-center align-items-center h-100",
                        )
                    ],
                ),
                color="light",
                className="shadow-sm rounded card-style bg-light",
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H6(
                                    "Total Budget",
                                    className="text-muted",
                                ),
                                html.H2(
                                    "€0.00",
                                    id="azure-costs-total-budget",
                                    className="card-text",
                                ),
                            ],
                            className="d-flex flex-column justify-content-center align-items-center h-100",
                        )
                    ]
                ),
                color="light",
                className="shadow-sm rounded card-style bg-light",
            ),
            width=4,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H6(
                                    "Number of Applications",
                                    className="text-muted",
                                ),
                                html.H2(
                                    "0",
                                    id="azure-costs-number-apps",
                                    className="card-text",
                                ),
                            ],
                            className="d-flex flex-column justify-content-center align-items-center h-100",
                        )
                    ]
                ),
                className="shadow-sm rounded card-style bg-light",
            ),
            width=4,
        ),
    ],
    className="my-4",
)

metrics_row_middle = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="azure-costs-histogram",
                className="shadow-sm rounded bg-light",
            ),
            width=8,
        ),
        dbc.Col(
            dcc.Graph(
                id="azure-costs-pie-chart",
                className="shadow-sm rounded bg-light",
            ),
            width=4,
        ),
    ],
    className="my-2",
)
