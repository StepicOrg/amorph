from enum import Enum


class MatchKind(Enum):
    ROOT_ROOT = 1
    CHILD_ROOT = 2
    ROOT_CHILD = 3


class PatchKind(Enum):
    EDIT = 1
    INSERT_UNDER = 2
    INSERT_ABOVE = 3
    DELETE_NODE = 4
    DELETE_SUBTREE = 5
