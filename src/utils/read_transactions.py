import pandas as pd
import datetime
import sys
import sqlite3


def reading_transactions(path, path_to_db):
    df_transactions = pd.read_csv(path, parse_dates=['Datum'], dayfirst=True).drop(columns=['Order Id', 'Tijd'])
    df_transactions.index = df_transactions['Datum']
    df_transactions = df_transactions.sort_index().rename({'Unnamed: 6': 'Local currency'}, axis=1)
    start_date = df_transactions['Datum'].min()
    date_rng = pd.date_range(start=start_date, end=datetime.datetime.today(), freq='B', name='Date')
    df_portfolio = pd.DataFrame()
    for date in date_rng:
        # Fill in portfolio
        df_day_transactions = df_transactions.loc[:date]
        df_sum_stocks = df_day_transactions.groupby(['Product', 'ISIN', 'Local currency']).agg(
            {'Aantal': 'sum', 'Koers': 'mean', 'Lokale waarde': 'sum', 'Waarde': 'sum', 'Wisselkoers': 'mean',
             'Kosten': 'sum', 'Totaal': 'sum'}).reset_index()
        df_sum_stocks['date'] = date
        df_portfolio = df_portfolio.append(df_sum_stocks)

    df_expenses = abs(df_portfolio.groupby('date')['Totaal'].sum())

    # Store tables in DB
    with sqlite3.connect(path_to_db) as con:
        df_portfolio.to_sql("daily_stocks", con, if_exists='replace')
        df_expenses.to_sql("daily_expense", con, if_exists='replace')


if __name__ == '__main__':
    transactions_path = sys.argv[1]
    db_path = sys.argv[2]
    reading_transactions(transactions_path, db_path)
