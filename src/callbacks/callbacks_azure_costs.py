import logging
import os

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from dashboards.models import AzureCosts
from layouts.sidebar import sidebar
from utils.database import Database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.callback(
    Output("azure-costs-histogram", "figure"),
    Output("azure-costs-pie-chart", "figure"),
    Output("azure-costs-total-costs", "children"),
    Output("azure-costs-total-budget", "children"),
    Output("azure-costs-number-apps", "children"),
    Input("azure-costs-date-range", "start_date"),
    Input("azure-costs-date-range", "end_date"),
    Input("azure-costs-devtst-checkbox", "value"),
    Input("azure-costs-acc-checkbox", "value"),
    Input("azure-costs-prd-checkbox", "value"),
    Input("azure-costs-application-select", "value"),
    Input("azure-costs-cluster-select", "value"),
)
def update_azure_costs(
    start_date,
    end_date,
    devtst_checked,
    acc_checked,
    prd_checked,
    selected_apps,
    selected_clusters,
):
    df = 

    # filter date range
    df["date"] = pd.to_datetime(df["date"])
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # filter by environment based on the checkboxes
    selected_envs = []
    if devtst_checked:
        selected_envs.extend(["dev", "tst", "devtst", "devtest"])
    if acc_checked:
        selected_envs.append("acc")
    if prd_checked:
        selected_envs.append("prd")
    df = df[df["environment"].isin(selected_envs)]

    # filter by cluster
    if selected_clusters and "all" not in selected_clusters:
        df = df[df["cluster"].isin(selected_clusters)]

    # filter by application
    if selected_apps and "all" not in selected_apps:
        df = df[df["application"].isin(selected_apps)]

    # Generate figures
    hist_fig = px.histogram(
        df,
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
        xaxis_title="Total Cost",
        yaxis_title="Application",
        title_x=0.5,
    )

    pc_fig = px.pie(
        df,
        names="application",
        values="cost",
        title="Cost Distribution by Application",
        color_discrete_sequence=px.colors.sequential.PuBu,
        hole=0.4,
    )
    pc_fig.update_layout(template="plotly_white", title_x=0.5)

    # Calculate total costs
    total_costs_text = f"€{df['cost'].sum():,.2f}"
    # Calculate total budget
    total_budget_text = f"€{25000:,.2f}"  # Assuming static budget value here
    # Calculate number of tracked applications
    num_of_apps = df["application"].nunique()

    return hist_fig, pc_fig, total_costs_text, total_budget_text, num_of_apps
