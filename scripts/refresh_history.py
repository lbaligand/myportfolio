from src.db_backend import DBBackend
from src.history import daily_prices, daily_portfolio
from src.transactions import degiro_transactions
from src.utils import connect_degiro


def refresh_history():
    backend = DBBackend()

    degiro_conn = connect_degiro()

    df_transactions = degiro_transactions(backend, degiro_conn=degiro_conn, store=True)

    df_yf = daily_prices(backend, df_transactions=df_transactions, store=True)

    daily_portfolio(backend, df_transactions=df_transactions, df_yf=df_yf, degiro_conn=degiro_conn, store=True)


if __name__ == '__main__':
    refresh_history()
