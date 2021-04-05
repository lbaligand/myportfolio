import os
import sys

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages.dashboard import dashboard_layout

app.layout = html.Div(children=[dcc.Location(id='url', refresh=True),
                                html.Div(id='page-content')])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """
    """
    if pathname == '/':
        return dashboard_layout
    else:
        return '404'


if __name__ == '__main__':
    sys.path.append(os.getcwd())
    app.run_server(host='0.0.0.0',
                   port=8050,
                   debug=True)
