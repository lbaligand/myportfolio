import json
import logging

import degiroapi

from dash_app.config import DEGIRO_PATH

logger = logging.getLogger()


def connect_degiro():
    """Creates a degiro connection"""
    logger.info("Connecting to DeGiro...")
    degiro = degiroapi.DeGiro()
    with open(DEGIRO_PATH) as f:
        d = json.load(f)
        degiro.login(d['username'], d['password'])

    return degiro
