import string

from unidecode import unidecode_expect_nonascii


def capitalize_name(place: str) -> str:
    return string.capwords(place)


def remove_accents(place: str) -> str:
    return unidecode_expect_nonascii(place)
