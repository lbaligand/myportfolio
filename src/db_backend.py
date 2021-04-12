"""
Contains class definition for database backend. Has utility functions.
Uses SQLAlchemy so that switching DBs is seamless
"""

import datetime
import logging

from sqlalchemy import create_engine, MetaData

from dash_app.config import DB_PATH, transaction_table

logger = logging.getLogger()


class DBBackend:
    def __init__(self):
        self.engine = create_engine(DB_PATH)
        self.connection = self.engine.connect()
        self.metadata = MetaData(bind=self.engine)
        self.start_date = self.start_date()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def path(self):
        """Return the path to the file that backs this database."""
        return self.path

    def start_date(self):
        """Return start date for which there is a data point"""
        ordered_dates = self.connection.execute(f'select distinct "date" from {transaction_table} order by "date" ASC')
        return datetime.datetime.fromisoformat(ordered_dates.fetchone()[0]).date()

    def close(self):
        """Close the connection to the database."""
        self.connection.close()
