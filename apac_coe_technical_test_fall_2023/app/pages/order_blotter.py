from time import sleep

import dash
import pandas as pd
import requests
from dash import Input, Output, State, callback, dash_table, dcc, html
from flask import session
from flask_login import current_user, logout_user

dash.register_page(__name__)


def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/getOrder",
            headers={"Authorization": f"Bearer {session['access_token']}"},
        )
        if response.status_code == 200:
            res = response.json()
            data: list[dict] = res["data"]
            timestamp: str = res["timestamp"]
            pagination: dict = res["pagination"]

            df = pd.DataFrame(data)

            return html.Div(
                [
                    html.H1("Order blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Br(),
                    dash_table.DataTable(
                        data=df.to_dict("records"),
                        columns=[{"name": col, "id": col} for col in df.columns],
                        page_action="custom",
                        page_current=pagination["currentPage"] - 1,
                        page_count=pagination["totalPages"],
                        id="order-blotter-table",
                    ),
                    html.Br(),
                    html.Div(children=timestamp, id="order-blotter-timestamp"),
                ]
            )
        if response.status_code == 401:
            logout_user()
            return html.Div(
                [
                    html.H1("Order blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Div(
                        children="Unauthorized, please login again.",
                        id="unauthorized-message",
                    ),
                ]
            )
        return html.Div(
            [
                html.H1("Order blotter"),
                dcc.Link("Go back to home", href="/"),
            ]
        )
    except Exception as e:
        return str(e)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("unauthorized-message", "children"),
    prevent_initial_call=True,
)
def redirect_after_logout(unauthorized_message):
    if unauthorized_message:
        sleep(1)
        return "/login"


@callback(
    Output("order-blotter-table", "data"),
    Output("order-blotter-timestamp", "children"),
    Input("order-blotter-table", "page_current"),
    State("order-blotter-table", "page_count"),
    prevent_initial_call=True,
)
def update_table(page_current: int, page_count: int):
    response = requests.get(
        "http://127.0.0.1:5000/api/getOrder",
        headers={"Authorization": f"Bearer {session['access_token']}"},
        params={"page": page_current + 1},
    )

    if response.status_code == 200:
        res = response.json()
        data: list[dict] = res["data"]
        timestamp: str = res["timestamp"]

        df = pd.DataFrame(data)
        return df.to_dict("records"), timestamp
