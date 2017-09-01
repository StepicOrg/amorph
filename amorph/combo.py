from . import diff, tokens, ast
from .utils import find_closest, empty_generator
from .metrics import string_similarity
from .exceptions import InvalidArgumentException
from enum import Enum


class Method(Enum):
    DIFF = 'diff'
    TOKENS = 'tokens'
    AST = 'ast'


def patch_with_closest(source, samples: list, method: Method = Method.DIFF, metric=string_similarity, key=None):
    matched_sample = find_closest(source, samples, metric, key)

    # no close sample found
    if matched_sample is None:
        return empty_generator()

    return patch_with_sample(source, matched_sample, method, key)


def patch_with_sample(source, sample, method: Method = Method.DIFF, key=None):
    if key:
        source = key(source)
        sample = key(sample)

    if not isinstance(method, Method):
        raise InvalidArgumentException('Unknown method {!r}'.format(method))

    if method == Method.DIFF:
        return diff.get_patches(source, sample)
    elif method == Method.TOKENS:
        return tokens.get_patches(source, sample)
    elif method == Method.AST:
        return ast.get_patches(source, sample)
