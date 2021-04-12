import os

basedir = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(os.path.dirname(basedir), "data")
DEGIRO_PATH = os.path.join(os.path.dirname(basedir), "degiro_creds.json")
EXCHANGE_MAPPING_PATH = os.path.join(DATA_PATH, "raw/exchange_symbol_map.json")
# Path to DB with SQLAlchemy syntax:
# Refer to https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
DB_PATH = "dialect+driver://username:password@host:port/database"

degiro_config_url = "https://trader.degiro.nl/product_search/config/dictionary/"

BASE_CURRENCY = 'EUR'

# DB format
transaction_table = 'transactions'

dict_logins = {
    'user': '123',
    'admin': 'admin'
}
