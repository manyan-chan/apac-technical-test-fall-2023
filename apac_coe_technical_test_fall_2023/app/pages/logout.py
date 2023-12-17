from time import sleep

import dash
from dash import Input, Output, callback, html
from flask import session
from flask_login import current_user, logout_user

dash.register_page(__name__)


def layout():
    if current_user.is_authenticated:
        logout_user()
        session.pop("access_token", None)
    return html.Div(
        children="You have been logged out - Please login", id="logout-message"
    )


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-message", "children"),
    prevent_initial_call=True,
)
def redirect_after_logout(logout_message):
    if logout_message:
        sleep(1)
        return "/"  # Replace with the desired redirect URL
