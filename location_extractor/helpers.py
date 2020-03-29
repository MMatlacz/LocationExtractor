from unidecode import unidecode_expect_nonascii


def remove_accents(place: str) -> str:
    return unidecode_expect_nonascii(place)


def parse_query_param(param: str) -> str:
    return remove_accents(param.lower()).replace("'", "\\'")
