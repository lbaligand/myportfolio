# Reusable components like navbar/header, footer etc.
# ------------------------------------------------------------

import dash_html_components as html
import dash_bootstrap_components as dbc

header = dbc.Row(children=[
    dbc.Col(html.Img(src='/assets/logo.png',
                     height='30px'),
            width='auto',
            align="center"),
    dbc.Col('MyPortfolio',
            className="h1 text-uppercase font-weight-bold",
            width=True,
            align="center"),
    ],
                 className='p-3 bg-dark text-white',
                 style={'fontFamily': 'Inconsolata'})
