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
from utils.database import Database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
load_dotenv()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

db = Database(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)


def fetch_azure_costs_data(date):
    try:
        query = select(AzureCosts).filter(AzureCosts.date == date)
        with db.get_session() as session:
            df = pd.read_sql(query, session.bind)
        return df
    except SQLAlchemyError as e:
        logger.error(f"Error fetching data from AzureCosts: {str(e)}")
        return pd.DataFrame()


df = fetch_azure_costs_data(date(2024, 10, 22))
df["date"] = pd.to_datetime(df["date"])


content = html.Div(
    [
        html.Div(id="load", style={"diplay": "none"}),
        dcc.DatePickerRange(
            id="azure-costs-date-picker-range",
            start_date=df["date"].min(),
            end_date=df["date"].max(),
            display_format="YYYY-MM-DD",
            style={"padding": "10px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        html.H5(
                                            "Total Costs",
                                            className="card-title",
                                            style={"font-size": "1rem"},
                                        ),
                                        html.P(
                                            id="azure-total-costs",
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
            style={"marginBottom": "20px"},
        ),
        html.Div(
            [
                dcc.Graph(
                    id="azure-costs-histogram",
                    style={"flex": "2", "marginRight": "20px"},
                ),
                dcc.Graph(id="azure-costs-pie-chart", style={"flex": "1"}),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
            },
        ),
        dash_table.DataTable(
            id="costs-table",
            columns=[
                {"name": i, "id": i} for i in ["resource_group", "application", "cost"]
            ],
            page_size=10,
            style_table={"overflowX": "auto"},
            sort_action="native",
            style_header={"backgroundColor": "white", "fontWeight": "bold"},
            style_cell={"padding": "5px", "textAlign": "center"},
            style_cell_conditional=[
                {"if": {"column_id": "resourceGroup"}, "width": "30%"},
                {"if": {"column_id": "application"}, "width": "20%"},
                {"if": {"column_id": "cost"}, "width": "20%"},
            ],
            style_data={"backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#e9ecef"}
            ],
        ),
    ],
    style={"marginLeft": "18rem", "marginRight": "2rem", "padding": "2rem 1rem"},
)

app.layout = html.Div([sidebar, content])


@app.callback(
    Output("azure-costs-histogram", "figure"),
    Output("azure-costs-pie-chart", "figure"),
    Output("azure-total-costs", "children"),
    Output("azure-total-budget", "children"),
    Output("azure-number-apps", "children"),
    Output("costs-table", "data"),
    Input("azure-costs-date-picker-range", "start_date"),
    Input("azure-costs-date-picker-range", "end_date"),
)
def update_azure_costs(start_date, end_date):
    filtered_df = df[
        (df["date"] >= pd.to_datetime(start_date))
        & (df["date"] <= pd.to_datetime(end_date))
    ]
    hist_fig = px.histogram(
        filtered_df,
        y="application",
        x="cost",
        histfunc="sum",
        title="Total Costs by Application",
        labels={"application": "Application", "cost": "Total Cost"},
        color_discrete_sequence=["#636EFA"],
        orientation="h",
    )

    hist_fig.update_layout(
        template="plotly_white",
        xaxis_title="Application",
        yaxis_title="Total Cost",
        title_x=0.5,
    )

    pc_fig = px.pie(
        filtered_df,
        names="application",
        values="cost",
        title="Cost Distribution by Application",
        color_discrete_sequence=px.colors.sequential.PuBu,
        hole=0.4,
    )

    pc_fig.update_layout(template="plotly_white", title_x=0.5)

    # calculate total costs
    total_costs_text = f"€{filtered_df['cost'].sum():,.2f}"
    # calculat total budget
    total_budget_text = f"€{25000:,.2f}"
    # calculate number of tracked applications
    num_of_apps = filtered_df["application"].nunique()

    # Aggregate costs by resource group
    rg_sorted = (
        filtered_df.groupby(["resource_group", "application"])["cost"]
        .sum()
        .reset_index()
    )
    rg_sorted_table = rg_sorted.sort_values(by="cost", ascending=False).to_dict(
        "records"
    )

    return (
        hist_fig,
        pc_fig,
        total_costs_text,
        total_budget_text,
        num_of_apps,
        rg_sorted_table,
    )


@app.callback(Output("access-pages", "children"), [Input("load", "children")])
def load_access_pages(temp):
    access_pages = []
    access_pages.append(
        dbc.NavLink("Just Invoice", href="/justinvoice", active="exact")
    )
    access_pages.append(
        dbc.NavLink("Just Request", href="/justrequest", active="exact")
    )
    access_pages.append(dbc.NavLink("67ter", href="/67ter", active="exact"))
    access_pages.append(
        dbc.NavLink("Contestations", href="/contestation", active="exact")
    )
    access_pages.append(dbc.NavLink("JustSend", href="/justsend", active="exact"))
    access_pages.append(dbc.NavLink("JustFine", href="/justfine", active="exact"))
    access_pages.append(dbc.NavLink("JustView", href="/justview", active="exact"))
    return access_pages


if __name__ == "__main__":
    server.run(debug=True)
