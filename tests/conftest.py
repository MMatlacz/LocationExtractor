import os

import pytest

from location_extractor.clients import DBClient
from location_extractor.named_entity_recognition.ner import NERExtractor
from location_extractor.extractor import Extractor


@pytest.fixture(scope='session')
def location_extractor():
    return Extractor()


@pytest.fixture(scope='session')
def ner_extractor():
    return NERExtractor()


@pytest.fixture(scope='session')
def dbclient():
    client = DBClient()
    yield client
    if os.path.exists(client.dbpath):
        os.remove(client.dbpath)
