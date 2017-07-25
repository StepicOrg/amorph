from . import diff, tokens
from .utils import find_closest, empty_generator
from .metrics import string_similarity
from .exceptions import InvalidArgumentException
from enum import Enum


class Method(Enum):
    DIFF = 'diff'
    TOKENS = 'tokens'


def patch_with_closest(source: str, samples: list, method: Method = Method.DIFF, metric=string_similarity):
    matched_sample = find_closest(source, samples, metric)

    # no sample close sample found
    if matched_sample is None:
        return empty_generator()

    return patch_with_sample(source, matched_sample, method)


def patch_with_sample(source: str, sample: str, method: Method = Method.DIFF):
    if not isinstance(method, Method):
        raise InvalidArgumentException('Unknown method {!r}'.format(method))

    if method == Method.DIFF:
        return diff.get_patches(source, sample)
    elif method == Method.TOKENS:
        return tokens.get_patches(source, sample)
