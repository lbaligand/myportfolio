import logging
from datetime import date

import pandas as pd

from dash_app.config import transaction_table
from src.utils import connect_degiro

logger = logging.getLogger()


def degiro_transactions(backend, degiro_conn=None, store=False):
    if not degiro_conn:
        degiro_conn = connect_degiro()
    from_date = date(1900, 1, 1)
    to_date = date.today()
    logger.info(f"Getting transactions from {from_date} to {to_date}")
    df_transactions = pd.DataFrame(degiro_conn.transactions(from_date=from_date, to_date=to_date))

    if store:
        logger.info(f"Storing transactions into {backend.path}")
        df_transactions.to_sql(name=transaction_table, con=backend.engine, if_exists='replace', index=False)
        logger.info(f"Closing DB.")
        backend.close()
    return df_transactions
