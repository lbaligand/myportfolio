import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app import app
from dash.dependencies import Input, Output

from dash_app import config
from dash_app.pages.components import header
from scripts.refresh_history import refresh_history
from src.db_backend import SQLiteBackend

refresh_history()
backend = SQLiteBackend()
df_portfolio_total = pd.read_sql("daily_portfolio_total", parse_dates='Date', con=backend.engine)
df_portfolio_stocks = pd.read_sql("daily_portfolio_stocks", parse_dates='Date', con=backend.engine)


@app.callback(Output('portfolio-indicator', 'figure'),
              [Input('interval-component', 'n_intervals')])
def show_indicator(n):
    # indicator
    value = df_portfolio_total['total_base_currency'].iloc[-1]
    reference = abs(df_portfolio_total['totalPlusFeeInBaseCurrency'].iloc[-1])

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=value,
        number={'prefix': f"{config.BASE_CURRENCY} ", 'valueformat': ",.2f"},
        delta={'position': "top", 'reference': reference, 'relative': True, 'valueformat': '.2%'},
        domain={'x': [0, 1], 'y': [0, 1]}))

    return fig


@app.callback(Output('portfolio-overview', 'figure'),
              [Input('interval-component', 'n_intervals')])
def plot_total_portfolio(n):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_portfolio_total.Date, y=df_portfolio_total['total_base_currency'], mode='lines'))

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    return fig


@app.callback(Output("stack-overview", 'figure'),
              [Input('interval-component', 'n_interval')])
def plot_stack_portofolio(n):
    fig = go.Figure()
    for ticker in df_portfolio_stocks.yf_ticker.unique():
        df_ticker = df_portfolio_stocks[df_portfolio_stocks['yf_ticker'] == ticker]
        fig.add_trace(go.Scatter(
            x=df_ticker.Date, y=df_ticker['total_base_currency'],
            name=ticker,
            hoverinfo='x+y',
            mode='lines',
            line=dict(width=0.5),
            stackgroup='one'  # define stack group
        ))

    return fig


@app.callback(Output("pie-overview", 'figure'),
              [Input('interval-component', 'n_interval')])
def plot_pie_stocks(n):
    df_last_date = df_portfolio_stocks[df_portfolio_stocks.Date == df_portfolio_stocks.Date.iloc[-1]]
    fig = px.pie(df_last_date, values='total_base_currency', names='yf_ticker',
                 hover_data=['yf_ticker'], labels={'yf_ticker': 'Yahoo Finance Ticker'})
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


# ----------------------------------------------------------------------
# WIDGET 1
# ----------------------------------------------------------------------
widget_1 = html.Div(children=[
    dcc.Graph(id='portfolio-indicator', animate=True),
    dcc.Graph(id='portfolio-overview', animate=True),
    dcc.Graph(id='stack-overview', animate=True),
    dcc.Graph(id='pie-overview', animate=True),
    dcc.Interval(id='interval-component', n_intervals=0, interval=60 * 1000)
], id='widget_1')

# assemble components into layout
dashboard_layout = html.Div([
    header,
    widget_1
])
