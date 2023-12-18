import json
from time import sleep

import dash
import pandas as pd
import plotly.express as px
import requests
from dash import Input, Output, State, callback, dcc, html
from flask import session
from flask_login import current_user, logout_user

dash.register_page(__name__)


def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/getCommission",
            headers={"Authorization": f"Bearer {session['access_token']}"},
        )
        if response.status_code == 200:
            res = response.json()
            data: list[dict] = res["data"]
            timestamp: str = res["timestamp"]

            return html.Div(
                [
                    html.H1("Commission blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        id="dropdown",
                        options=[
                            {"label": "Trader", "value": "Trader"},
                            {"label": "Instrument", "value": "Instrument_Code"},
                            {"label": "Counterparty", "value": "Counterparty"},
                        ],
                        value="Trader",
                        clearable=False,
                    ),
                    html.Br(),
                    dcc.Graph(
                        id="commission-graph",
                    ),
                    html.Br(),
                    html.Div(children=timestamp),
                    dcc.Store(id="intermediate-value", data=json.dumps(data)),
                ]
            )
        if response.status_code == 401:
            logout_user()
            return html.Div(
                [
                    html.H1("Commission blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Div(
                        children="Unauthorized, please login again.",
                        id="commission-blotter-unauth",
                    ),
                ]
            )
        return html.Div(
            [
                html.H1("Commission blotter"),
                dcc.Link("Go back to home", href="/"),
            ]
        )
    except Exception as e:
        return str(e)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("commission-blotter-unauth", "children"),
    prevent_initial_call=True,
)
def redirect_after_logout(unauthorized_message):
    if unauthorized_message:
        sleep(1)
        return "/login"


@callback(
    Output("commission-graph", "figure"),
    Input("dropdown", "value"),
    State("intermediate-value", "data"),
)
def update_graph(dropdown: str, data: str):
    df = pd.DataFrame(json.loads(data))
    df["Commission"] = df["Commission"].astype(float)
    fig = px.bar(df, x=dropdown, y="Commission", title="Traded Commissions")
    return fig
