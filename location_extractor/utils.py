import jellyfish


def fuzzy_match(s1, s2, max_dist=6):
    return jellyfish.levenshtein_distance(s1, s2) <= max_dist
