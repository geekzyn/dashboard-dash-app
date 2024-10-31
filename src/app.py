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

from dashboards.models import AzureCosts
from utils.database import Database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
load_dotenv()

db = Database(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server


def fetch_azure_costs_dashboard_parameters():
    # fetch parametrs to initialize dashboard data
    try:
        with db.get_session() as session:
            applications = session.query(AzureCosts.application).distinct().all()
            clusters = session.query(AzureCosts.cluster).distinct().all()
            environments = session.query(AzureCosts.environment).distinct().all()
            min_date = (
                session.query(AzureCosts.date)
                .order_by(AzureCosts.date.asc())
                .first()[0]
            )
            max_date = (
                session.query(AzureCosts.date)
                .order_by(AzureCosts.date.desc())
                .first()[0]
            )
        # convert list of tuples to list of strings
        applications = [app[0] for app in applications if app[0]]
        clusters = [cluster[0] for cluster in clusters if cluster[0]]
        # ['devtst', 'prd', 'acc', 'devtest', 'tst', 'dev'] => ['devtst', 'acc', 'prd']
        environments = ["devtst", "acc", "prd"]
    except SQLAlchemyError as e:
        logger.error(f"Error fetching filter options: {str(e)}")
        applications, clusters, environments, min_date, max_date = (
            [],
            [],
            [],
            None,
            None,
        )
    return applications, clusters, environments, min_date, max_date


unique_apps, unique_clusters, unique_envs, min_date, max_date = (
    fetch_azure_costs_dashboard_parameters()
)


def fetch_azure_costs_data(start_date, end_date):
    # fetch azure costs data
    try:
        query = select(AzureCosts).where(
            (AzureCosts.date >= start_date) & (AzureCosts.date <= end_date)
        )
        with db.get_session() as session:
            df = pd.read_sql(query, session.bind)
        return df
    except SQLAlchemyError as e:
        logger.error(f"Error fetching data from AzureCosts: {str(e)}")
        return pd.DataFrame()


logger.info("Fetch all Azure Costs data.")
df_all = fetch_azure_costs_data(min_date, max_date)


app.layout = html.Div([dcc.Store(id="azure-costs-data-store"), sidebar, content])


if __name__ == "__main__":
    server.run(debug=True)
