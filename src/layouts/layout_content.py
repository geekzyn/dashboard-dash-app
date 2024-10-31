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
from layouts.sidebar import sidebar
from utils.database import Database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

content = html.Div(
    [
        html.Div(
            [azure_costs_filters],
            className="shadow-sm rounded card-style bg-light p-4",
        ),
        metrics_row_top,
        metrics_row_middle,
    ],
    className="p-4",
    style={"margin-left": "250px"},
)
