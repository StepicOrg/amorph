from . import diff
from .utils import find_closest, empty_generator
from .metrics import string_similarity
from .exceptions import InvalidArgumentException
from enum import Enum


class Method(Enum):
    DIFF = 'diff'


def patch_with_closest(source: str, samples: list, method: Method = Method.DIFF, metric=string_similarity):
    if not isinstance(method, Method):
        raise InvalidArgumentException('Unknown method {!r}'.format(method))

    matched_sample = find_closest(source, samples, metric)

    # no sample close sample found
    if matched_sample is None:
        return empty_generator()

    if method == Method.DIFF:
        return diff.get_patches(source, matched_sample)
