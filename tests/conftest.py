import pytest

from location_extractor.named_entity_recognition.ner import NERExtractor
from location_extractor.named_entity_recognition.geograpy_nltk import download_nltk
from location_extractor.extractor import Extractor

download_nltk()


@pytest.fixture(scope="session")
def location_extractor():
    return Extractor()


@pytest.fixture(scope="session")
def ner_extractor():
    return NERExtractor()
