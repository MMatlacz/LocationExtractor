import jellyfish


def fuzzy_match(s1, s2, max_dist=6):
    print(jellyfish.levenshtein_distance(s1, s2))
    return jellyfish.levenshtein_distance(s1, s2) <= max_dist
