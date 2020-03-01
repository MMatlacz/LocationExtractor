from typing import List

import nltk


class NERExtractor:
    def find_entities(self, text) -> List[str]:
        text = nltk.word_tokenize(text)
        named_entities = nltk.ne_chunk(nltk.pos_tag(text))

        places = []
        for named_entity in named_entities:
            if type(named_entity) is nltk.tree.Tree:
                if named_entity.label() in {'GPE', 'PERSON', 'ORGANIZATION'}:
                    found_place = ' '.join([leaf[0] for leaf in named_entity.leaves()])
                    places.append(found_place)

        return places
