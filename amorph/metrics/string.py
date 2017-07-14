from difflib import SequenceMatcher


def string_similarity(source: str, sample: str):
    matcher = SequenceMatcher(None, source, sample)

    return matcher.quick_ratio()
