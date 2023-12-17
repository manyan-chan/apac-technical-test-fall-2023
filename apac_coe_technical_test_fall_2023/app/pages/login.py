from time import sleep

import dash
import requests
from dash import Input, Output, State, callback, dcc, html
from flask import session
from flask_login import login_user

from apac_coe_technical_test_fall_2023.app.user import User

dash.register_page(__name__)


# Login screen
layout = html.Div(
    [
        html.H2("Please log in to continue:", id="h1"),
        dcc.Input(placeholder="Enter your username", type="text", id="uname-box"),
        dcc.Input(placeholder="Enter your password", type="password", id="pwd-box"),
        html.Button(children="Login", n_clicks=0, type="submit", id="login-button"),
        html.Div(children="", id="output-state"),
        html.Br(),
        dcc.Link("Home", href="/"),
    ]
)


@callback(
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
)
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        try:
            response = requests.post(
                "http://127.0.0.1:5000/auth/login",
                data={"username": username, "password": password},
            )
            if response.status_code == 200:
                session["access_token"] = response.json()["access_token"]
                login_user(User(username))
                return "Login Successful"
            return "Login Failed"
        except Exception as e:
            return str(e)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("output-state", "children"),
    prevent_initial_call=True,
)
def redirect_after_login(output_state):
    if output_state == "Login Successful":
        sleep(1)
        return "/"
