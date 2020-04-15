import os
import pickle
from typing import List
from urllib.request import urlopen

import spacy
from urllib3 import HTTPResponse

from location_extractor import src_dir
from location_extractor.containers import Location


class NERExtractor:
    def __init__(self):
        self.model_path = os.path.join(src_dir, 'data', 'nlp.pkl')
        self.url = 'https://github.com/MMatlacz/LocationExtractor/releases/download/v1.0.1/nlp.pkl'
        if not os.path.exists(self.model_path):
            self.download_model()
        self.nlp: spacy.language.Language = pickle.load(open(self.model_path, 'rb'))

    def download_model(self) -> None:
        with open(self.model_path, 'wb') as nlp:
            response: HTTPResponse = urlopen(self.url)
            nlp.write(response.read())

    def find_entities(self, text) -> List[Location]:
        places = []
        for named_entity in self.nlp(text).ents:
            if named_entity.label_ in {'COUNTRY', 'STATE', 'CITY', 'REGION', 'CONTINENT'}:
                places.append(Location(name=named_entity.text.strip(), type=named_entity.label_))

        return places
