import dash
from dash import html, dcc

dash.register_page(__name__, path="/")


layout = html.Div(
    [
        dcc.Link("Go to Order Blotter", href="/order-blotter"),
        html.Br(),
        dcc.Link("Go to Trade Blotter", href="/trade-blotter"),
    ]
)
