import ast
import logging
from typing import List, Tuple, Optional

from .constants import MatchKind
from .models import (Tree, PatchDelete,
                     PatchInsertAbove, PatchEdit, PatchInsertUnder, Patch)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s %(asctime)s %(levelname)s %(message)s')


def match_two_ast_nodes(left: ast.AST, right: ast.AST) -> bool:
    if type(left) != type(right):
        return False

    for field in left._fields:
        left_item = getattr(left, field)
        right_item = getattr(right, field)

        if not isinstance(left_item, ast.AST) and \
           not isinstance(right_item, ast.AST) and \
           left_item != right_item:
            return False

    return True


def match_two_tree(left_tree: Tree, right_tree: Tree, res=None):
    if res is None:
        res = {}

    cached_value = res.get((left_tree, right_tree))
    if cached_value is not None:
        return cached_value[0], cached_value[1], res

    ast_nodes_matched = match_two_ast_nodes(left_tree.node, right_tree.node)

    # if roots matched we already have one match pair
    roots_matches = int(ast_nodes_matched)
    n_nodes = roots_matches
    kind = MatchKind.ROOT_ROOT
    ind = roots_matches

    # NOTE: Known bug. Algorithm must compare all possible pairs
    #       This version is used for simplicity and speed
    for l, r in zip(left_tree.children, right_tree.children):
        n, _, _ = match_two_tree(l, r, res)
        n_nodes += n

    for i, right_child in enumerate(right_tree.children):
        n, _, _ = match_two_tree(left_tree, right_child, res)
        if n > n_nodes:
            n_nodes = n
            kind = MatchKind.ROOT_CHILD
            ind = i

    for i, left_child in enumerate(left_tree.children):
        n, _, _ = match_two_tree(left_child, right_tree, res)
        if n > n_nodes:
            n_nodes = n
            kind = MatchKind.CHILD_ROOT
            ind = i

    res[(left_tree, right_tree)] = (n_nodes, (kind, ind))
    return n_nodes, (kind, ind), res


def get_patches(left_tree: Tree, right_tree: Tree, res: dict, patches: list = None) -> List[Patch]:
    if patches is None:
        patches = []
    _, (kind, ind) = res.get((left_tree, right_tree))
    if kind == MatchKind.ROOT_ROOT:
        if len(left_tree.children) > len(right_tree.children):
            not_deleted_descendants = list(range(len(left_tree.children)))
            patches.append(PatchDelete(tree=left_tree,
                                       delete_root=False,
                                       not_deleted_descendants=not_deleted_descendants))

        if len(right_tree.children) > len(left_tree.children):
            inserted_trees = right_tree.children[len(left_tree.children):]
            patches.append(PatchInsertUnder(node=left_tree,
                                            inserted_trees=inserted_trees))

        if ind == 0:
            patches.append(PatchEdit(node_from=left_tree, node_to=right_tree))

        for l, r in zip(left_tree.children, right_tree.children):
            patches = get_patches(l, r, res, patches)

        return patches
    elif kind == MatchKind.ROOT_CHILD:
        if (patches
            and isinstance(patches[-1], PatchInsertAbove)
            and left_tree == patches[-1].node):
            patches[-1].new_child_position.append(ind)
        else:
            patches.append(PatchInsertAbove(node=left_tree,
                                            inserted_tree=right_tree,
                                            new_child_position=[ind]))
        return get_patches(left_tree, right_tree.children[ind], res, patches)
    elif kind == MatchKind.CHILD_ROOT:
        if (patches
            and isinstance(patches[-1], PatchDelete)
            and is_descendant(left_tree, patches[-1].tree)):
            patches[-1].not_deleted_descendants.append(ind)
        else:
            not_deleted_descendants = [ind]
            patches.append(PatchDelete(tree=left_tree,
                                       delete_root=True,
                                       not_deleted_descendants=not_deleted_descendants))
        return get_patches(left_tree.children[ind], right_tree, res, patches)

    assert False, f'unknown kind: {kind}'


def pretty_print_tree(tree: Tree, indent=' ' * 2) -> str:
    def _pretty_print_tree(tr: Tree, lvl: int, cur_res: List[str]):
        cur_res.append(f'{lvl*indent}{tr.name}')
        for child in tr.children:
            _pretty_print_tree(child, lvl + 1, cur_res)
        return

    list_of_lines = []
    _pretty_print_tree(tree, 0, list_of_lines)
    return '\n'.join(list_of_lines)


def get_description_of_changes(left_code: str, right_code: str) -> List[Tuple[str, int]]:
    left_ast = ast.parse(left_code)
    right_ast = ast.parse(right_code)

    logger.debug('\n%s\n%s', left_code, ast.dump(left_ast))
    logger.debug('\n%s\n%s', right_code, ast.dump(right_ast))

    left_tree = Tree(left_ast)
    right_tree = Tree(right_ast)

    logger.debug('\n%s', pretty_print_tree(left_tree))
    logger.debug('\n%s', pretty_print_tree(right_tree))

    num, _, result = match_two_tree(left_tree, right_tree)

    patches = get_patches(left_tree, right_tree, result)

    return list(map(lambda patch: (patch.get_description(), patch.get_weight()), patches))


def is_descendant(descendant: Tree, ancestor: Tree) -> bool:
    while descendant is not None:
        if descendant in ancestor.children:
            return True
        descendant = descendant.parent
    return False


def get_child_by_path(root: Tree, path: List[int]) -> Optional[Tree]:
    if not path:
        return root

    try:
        child = root.children[path[0]]
        for pos in path[1:]:
            child = child.children[pos]
    except IndexError:
        child = None
    return child
