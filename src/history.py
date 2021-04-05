import datetime
import json
import logging

import pandas as pd
import requests
import yfinance as yf
from degiroapi.product import Product
from requests import RequestException

from dash_app.config import transaction_table, EXCHANGE_MAPPING_PATH, degiro_config_url, BASE_CURRENCY
from src.utils import connect_degiro

logger = logging.getLogger()


def exchange_suffix(path):
    """Reads mapping to create: {Exchange name: Yahoo Finance suffix}"""
    with open(path) as f:
        market2symbol = json.load(f)
        exchange2symbol = dict()
        for market_entry in market2symbol.values():
            exchange2symbol.update(market_entry)
    return exchange2symbol


def get_degiro_dict(path="https://trader.degiro.nl/product_search/config/dictionary/"):
    r = requests.get(path)
    if r.status_code == 200:
        return r.json()
    else:
        logger.error(f"{r.status_code} Error getting data from {path}")
        raise RequestException


def create_yfticker(row, exchange_suffix_map):
    suffix = exchange_suffix_map[row['exchangeId']]
    if suffix:
        return row['symbol'] + suffix
    else:
        return row['symbol']


def get_productid_mapping(degiro_ids):
    """Creates dictionary {productId (degiro): Ticker Symbol (Yahoo Finance)}"""
    logger.info("Connecting to DeGiro...")
    degiro = connect_degiro()

    logger.info("Lookup products info from DeGiro endpoint")
    df_info = {}
    for degiro_id in degiro_ids:
        df_info[degiro_id] = degiro.product_info(degiro_id)
    df_info = pd.DataFrame.from_dict(df_info).T
    exchange_ids = df_info['exchangeId'].unique()

    logger.info("Getting ExchangeId dictionary form DeGiro endpoint.")
    exch_dict = get_degiro_dict(path=degiro_config_url)['exchanges']

    logger.info("Getting Exchange suffix mapping {Exchange name: Yahoo Finance suffix}")
    exchange2symbol = exchange_suffix(path=EXCHANGE_MAPPING_PATH)

    id2symbol_exchange = {}
    for exchange_id in exchange_ids:
        # Get exchange name
        try:
            exchange_name = list(filter(lambda x: x["id"] == int(exchange_id), exch_dict))[0]['name']
        except IndexError:
            logger.info(
                f"Market id {exchange_id} not covered in degiro dictionary. Please checkout {degiro_config_url}")
            exchange_name = None

        # Get exchange symbol
        try:
            id2symbol_exchange[exchange_id] = exchange2symbol[exchange_name]
        except KeyError:
            logger.error(
                f"Exchange '{exchange_name}' not covered in mapping to symbol. Please checkout {EXCHANGE_MAPPING_PATH}")
            id2symbol_exchange[exchange_id] = None

    # Creates dictionary
    df_symbols = df_info[['exchangeId', 'symbol']].drop_duplicates()
    # replace outdated symbol in degiro to match witch new symbol in yfinance
    df_symbols['symbol'].replace({'ALS30': 'S30'}, inplace=True)
    df_symbols['yf_ticker'] = df_symbols.apply(create_yfticker, exchange_suffix_map=id2symbol_exchange, axis=1)
    return df_symbols['yf_ticker'].to_dict()


def get_history(yf_tickers, start_date):
    """
    Get tickers historical information from Yahoo finance
    :param yf_tickers: list of ticker symbols (as from yahoo finance)
    :param start_date: starting date of history
    :return: pandas dataframe with history as shape (day x (info, ticker))
    """
    logger.info(f'Retrieving history since {start_date} for: {yf_tickers}')
    df_hist = yf.download(' '.join(yf_tickers), start=start_date)
    return df_hist


def daily_prices(backend, df_transactions=None, store=False):
    if df_transactions is None:
        df_transactions = pd.read_sql(transaction_table, parse_dates=['date'], con=backend.engine)

    # get Ticker mapping {degiroID: YahooTicker}
    productIds = df_transactions['productId'].unique()
    degiro2yf_dict = get_productid_mapping(degiro_ids=productIds)

    # get Stock daily price history from Yahoo Finance
    df_yf = get_history(yf_tickers=list(degiro2yf_dict.values()), start_date=backend.start_date).loc[:, 'Close']

    if store:
        # store partial raw info from yahoo finance
        df_yf.to_sql("yahoo_daily_price_raw", con=backend.engine, if_exists='replace')
    return df_yf


def daily_portfolio(backend, df_transactions=None, df_yf=None, degiro_conn=None, store=False):
    if df_transactions is None:
        df_transactions = pd.read_sql(transaction_table, parse_dates=['date'], con=backend.engine)

    # invert sign when SELL
    df_transactions['count'] = df_transactions.apply(
        lambda x: x['quantity'] if (x['buysell'] == 'B') else -x['quantity'], axis=1)

    # cumulative count of number of stocks
    df_count = df_transactions.groupby(['productId']).cumsum()[['count', 'totalPlusFeeInBaseCurrency']]
    df_rol = pd.merge(df_count, df_transactions[['productId', 'date']], left_index=True, right_index=True)
    #df_rol.index = pd.to_datetime(df_rol['date'], utc=True).dt.date
    df_rol.index = pd.to_datetime(df_rol['date'], utc=True).dt.tz_localize(None)
    df_rol = df_rol.drop(columns=['date'])

    # append today's number of stocks
    count_end = df_transactions.groupby('productId').agg(
        {'count': 'sum', 'totalPlusFeeInBaseCurrency': 'sum'}).reset_index()
    count_end['date'] = datetime.datetime.today()
    count_end.index = count_end['date']
    count_end = count_end.drop(columns=['date'])
    df_rol = df_rol.append(count_end)
    df_rol.index = pd.to_datetime(df_rol.index)

    # resample daily for the daily portfolio
    df_rol.reset_index(inplace=True)
    df_rol.drop_duplicates(subset=['date', 'productId'], keep='last', inplace=True)
    df_rol.set_index('date', drop=True, inplace=True)
    df_count = df_rol.groupby('productId').resample('D').ffill().drop(columns='productId').reset_index()

    # get Ticker mapping {degiroID: YahooTicker}
    productIds = df_transactions['productId'].unique()
    degiro2yf_dict = get_productid_mapping(degiro_ids=productIds)
    df_count['yf_ticker'] = df_count['productId'].replace(degiro2yf_dict)
    df_count.reset_index(drop=False, inplace=True)
    df_count.rename(columns={'date': 'Date'}, inplace=True)

    # merge count with stock price
    if df_yf is None:
        df_yf = pd.read_sql('yahoo_daily_price_raw', parse_dates=['Date'], con=backend.engine)
    df_close = df_yf.stack().reset_index().rename(columns={'level_1': 'yf_ticker', 0: 'Close'})
    df_close_count = df_close.merge(df_count, on=['yf_ticker', 'Date'], how='right')

    # fill nan values for weekends & day offs
    df_yf_count = df_close_count.set_index(['yf_ticker', 'Date'])
    df2 = df_yf_count.reindex(pd.MultiIndex.from_product(df_yf_count.index.levels)).groupby(['yf_ticker']).fillna(
        method='ffill')

    # Fetch currency exchange history
    productid2currency = dict()
    for productId in productIds:
        productid2currency[productId] = Product(degiro_conn.product_info(productId)).currency
    currencies = set(productid2currency.values())
    df_currency = get_history([f'{currency}{BASE_CURRENCY}=X' for currency in currencies],
                              start_date=backend.start_date).loc[:, 'Close']
    df_currency[f'{BASE_CURRENCY}{BASE_CURRENCY}=X'] = 1
    df_currency = df_currency.resample('D').ffill()
    df2 = df2.reset_index().dropna()
    df2['fxRate'] = df2.apply(lambda row: df_currency.loc[str(row['Date'].date()),
                                                          f'{productid2currency[row["productId"]]}{BASE_CURRENCY}=X'],
                              axis=1)
    df_filled = df2.assign(total=(df2['Close'] * df2['count']))
    df_filled['total_base_currency'] = df_filled['total'] * df_filled['fxRate']
    df_portfolio = df_filled.groupby('Date').sum().reset_index()

    if store:
        df_filled.to_sql("daily_portfolio_stocks", con=backend.engine, if_exists='replace')
    if store:
        df_portfolio.to_sql("daily_portfolio_total", con=backend.engine, if_exists='replace')
    return df_filled
