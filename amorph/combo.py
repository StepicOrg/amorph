from . import diff
from .utils import find_closest
from .metrics import string_similarity

DIFF = 'diff'
AVAILABLE_METHODS = [DIFF]


def patch_with_closest(source, samples, method=DIFF, metric=string_similarity):
    if method not in AVAILABLE_METHODS:
        raise ValueError('Unknown method {!r}'.format(method))

    matched_sample = find_closest(source, samples, metric)

    if method == DIFF:
        return diff.get_patches(source, matched_sample)
