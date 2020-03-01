import jellyfish


def fuzzy_match(s1, s2, max_dist=.8):
    return jellyfish.jaro_distance(s1, s2) >= max_dist
