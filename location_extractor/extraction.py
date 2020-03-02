from typing import List

import nltk

from location_extractor.helpers import capitalize_name


class NERExtractor:
    @classmethod
    def find_entities(cls, text) -> List[str]:
        text = nltk.word_tokenize(text)
        named_entities = nltk.ne_chunk(nltk.pos_tag(text))

        places = []
        for named_entity in named_entities:
            if type(named_entity) is nltk.tree.Tree:
                if named_entity.label() in {'GPE', 'PERSON', 'ORGANIZATION'}:
                    found_place = ' '.join([leaf[0] for leaf in named_entity.leaves()])
                    places.append(found_place)

        places = list(map(capitalize_name, places))
        return places
