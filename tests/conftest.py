import os

import pytest

from location_extractor.clients import DBClient
from location_extractor.extractor import Extractor
from location_extractor.named_entity_recognition.geograpy_nltk import (
    download_nltk,
)
from location_extractor.named_entity_recognition.ner import NERExtractor

download_nltk()


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
