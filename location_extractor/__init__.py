import os

from location_extractor.named_entity_recognition.geograpy_nltk import (
    download_nltk,
)

download_nltk()

src_dir = os.path.dirname(__file__)
base_dir = os.path.dirname(src_dir)
