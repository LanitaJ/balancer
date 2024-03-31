import logging

from logging import getLogger, INFO
from elasticsearch import Elasticsearch
from cmreslogging.handlers import CMRESHandler

def configure_logging():
    logger = getLogger(__name__)
    logger.setLevel(INFO)

    es_handler = CMRESHandler(
        hosts=[{'host': 'localhost', 'port': 9200}],
        auth_type=CMRESHandler.AuthType.NO_AUTH,
        es_index_name="python-logs"
    )

    logger.addHandler(es_handler)
    return logger



def configure_logging():
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


