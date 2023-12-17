import dash
from dash import Input, Output, callback, dcc, html
from flask import Flask
from flask_login import LoginManager, current_user

from apac_coe_technical_test_fall_2023.app.user import User
from apac_coe_technical_test_fall_2023.settings import SECRET_KEY

# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=False,
    use_pages=True,
    suppress_callback_exceptions=True,
)
app.init_app(server)


# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY=SECRET_KEY)

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="user-status-header"),
        html.Hr(),
        dash.page_container,
    ]
)


@callback(
    Output("user-status-header", "children"),
    Input("url", "pathname"),
)
def update_authentication_status(pathname):
    if current_user.is_authenticated:
        return dcc.Link("logout", href="/logout")
    return dcc.Link("login", href="/login")


def start():
    app.run_server(debug=True, port=3000)


if __name__ == "__main__":
    app.run_server(debug=True, port=3000)
