from time import sleep

import dash
import requests
from dash import Input, Output, callback, dash_table, dcc, html
from flask import session
from flask_login import current_user, logout_user

dash.register_page(__name__)


def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    try:
        response = requests.get(
            "http://127.0.0.1:5000/api/getTrade",
            headers={"Authorization": f"Bearer {session['access_token']}"},
        )
        if response.status_code == 200:
            res = response.json()
            data: list[dict] = res["data"]
            timestamp: str = res["timestamp"]
            pagination: dict = res["pagination"]
            columns = [{"name": col, "id": col} for col in data[0].keys()]

            return html.Div(
                [
                    html.H1("Trade blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Br(),
                    dash_table.DataTable(
                        data=data,
                        columns=columns,
                        page_action="custom",
                        page_current=pagination["currentPage"] - 1,
                        page_count=pagination["totalPages"],
                        id="trade-blotter-table",
                    ),
                    html.Br(),
                    html.Div(children=timestamp, id="trade-blotter-timestamp"),
                ]
            )
        if response.status_code == 401:
            logout_user()
            return html.Div(
                [
                    html.H1("Trade blotter"),
                    dcc.Link("Go back to home", href="/"),
                    html.Br(),
                    html.Div(
                        children="Unauthorized, please login again.",
                        id="trade-blotter-unauth",
                    ),
                ]
            )
        return html.Div(
            [
                html.H1("Trade blotter"),
                dcc.Link("Go back to home", href="/"),
            ]
        )
    except Exception as e:
        return str(e)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("trade-blotter-unauth", "children"),
    prevent_initial_call=True,
)
def redirect_after_logout(unauthorized_message):
    if unauthorized_message:
        sleep(1)
        return "/login"


@callback(
    Output("trade-blotter-table", "data"),
    Output("trade-blotter-timestamp", "children"),
    Input("trade-blotter-table", "page_current"),
    prevent_initial_call=True,
)
def update_table(page_current: int):
    response = requests.get(
        "http://127.0.0.1:5000/api/getTrade",
        headers={"Authorization": f"Bearer {session['access_token']}"},
        params={"page": page_current + 1},
    )

    if response.status_code == 200:
        res = response.json()
        data: list[dict] = res["data"]
        timestamp: str = res["timestamp"]

        return data, timestamp
