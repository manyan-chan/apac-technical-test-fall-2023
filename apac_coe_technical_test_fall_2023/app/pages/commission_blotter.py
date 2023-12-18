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
            orders: list[dict] = res["data"]["orders"]
            trades: list[dict] = res["data"]["trades"]
            timestamp: str = res["timestamp"]

            return html.Div(
                [
                    html.H1("Commission blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        id="commission-blotter-dropdown",
                        options=[
                            {"label": "Trader", "value": "Trader"},
                            {"label": "Instrument", "value": "Instrument_Code"},
                            {"label": "Counterparty", "value": "Counterparty_Code"},
                        ],
                        value="Trader",
                        clearable=False,
                    ),
                    html.Br(),
                    dcc.Graph(
                        id="traded-commission-graph",
                    ),
                    html.Br(),
                    dcc.Graph(
                        id="expected-commission-graph",
                    ),
                    html.Div(children=timestamp),
                    dcc.Store(id="traded-commission-data", data=json.dumps(trades)),
                    dcc.Store(id="expected-commission-data", data=json.dumps(orders)),
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
    Output("traded-commission-graph", "figure"),
    Output("expected-commission-graph", "figure"),
    Input("commission-blotter-dropdown", "value"),
    State("traded-commission-data", "data"),
    State("expected-commission-data", "data"),
)
def update_graph(dropdown: str, trades: str, orders: str):
    df_trades = pd.DataFrame(json.loads(trades))
    df_trades["Commission"] = df_trades["Commission"].astype(float)

    df_orders = pd.DataFrame(json.loads(orders))
    df_orders["Commission"] = df_orders["Commission"].astype(float)

    fig_traded = px.bar(
        df_trades, x=dropdown, y="Commission", title="Traded Commissions"
    )
    fig_expected = px.bar(
        df_orders, x=dropdown, y="Commission", title="Expected Commissions"
    )
    return fig_traded, fig_expected
