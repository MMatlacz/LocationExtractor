import jellyfish

from unidecode import unidecode_expect_nonascii


def fuzzy_match(text1: str, text2: str, max_dist: int = 6) -> bool:
    return jellyfish.levenshtein_distance(text1, text2) <= max_dist


def remove_accents(place: str) -> str:
    return unidecode_expect_nonascii(place)


def parse_query_param(query_param: str) -> str:
    return remove_accents(query_param.lower()).replace("'", r"\'")
