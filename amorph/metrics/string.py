from difflib import SequenceMatcher


def string_similarity(source, sample):
    matcher = SequenceMatcher(None, source, sample)

    return matcher.quick_ratio()
