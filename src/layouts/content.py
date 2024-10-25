import dash_bootstrap_components as dbc
from dash import dcc, html

# Date picker
date_picker = dcc.DatePickerRange(
    id="date-picker",
    start_date="2024-01-01",
    end_date="2024-12-31",
    display_format="DD/MM/YYYY",
    className="date-picker",
)

# Environment filter buttons
environment_filter = dbc.ButtonGroup(
    [
        dbc.Button("DEV", id="env-dev", color="secondary", outline=True),
        dbc.Button("TST", id="env-tst", color="secondary", outline=True),
        dbc.Button("ACC", id="env-acc", color="secondary", outline=True),
        dbc.Button("PRD", id="env-prd", color="secondary", outline=True),
    ],
    className="mb-3",
)

# Application dropdown
application_dropdown = dcc.Dropdown(
    id="application-dropdown",
    options=[
        {"label": "All", "value": "all"}
    ],  # Add more options dynamically if needed
    value="all",
    className="application-dropdown",
)

# Cluster dropdown
cluster_dropdown = dcc.Dropdown(
    id="cluster-dropdown",
    options=[
        {"label": "All", "value": "all"}
    ],  # Add more options dynamically if needed
    value="all",
    className="cluster-dropdown",
)

# Main content layout with filters
content_layout = html.Div(
    [
        html.Div([html.H5("DATE"), date_picker], className="filter-section"),
        html.Div(
            [html.H5("ENVIRONMENT"), environment_filter], className="filter-section"
        ),
        html.Div(
            [html.H5("APPLICATION"), application_dropdown], className="filter-section"
        ),
        html.Div([html.H5("CLUSTER"), cluster_dropdown], className="filter-section"),
    ],
    className="content-area",
)
