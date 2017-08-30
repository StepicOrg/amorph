from difflib import SequenceMatcher
from .utils import metric_with_key


@metric_with_key
def string_similarity(source: str, sample: str):
    matcher = SequenceMatcher(None, source, sample)

    return matcher.quick_ratio()
