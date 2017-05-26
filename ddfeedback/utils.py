import ast
import logging
from typing import List, Iterable, Tuple

from .constants import MatchKind
from .models import (Identifier, Body, Targets, ListOfNodes, CallArgs, Tree, PatchDeleteNode,
                     PatchDeleteSubtree, PatchInsertAbove, PatchEdit, PatchInsertUnder, Patch, DecoratorList,
                     ClassBases, Keywords)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s %(asctime)s %(levelname)s %(message)s')

allowed_nodes = (ast.Module,
                 ast.BinOp,
                 ast.operator,
                 ast.Num,
                 ast.Name,
                 ast.Return,
                 ast.Expr,
                 ast.FunctionDef,
                 ast.arguments,
                 ast.arg,
                 ast.Call,
                 ast.expr_context,
                 ast.Assign,
                 ast.ClassDef,
                 ast.keyword,
                 ast.Delete,
                 ast.AugAssign,
                 Identifier,
                 ListOfNodes)


def check_node_type(node):
    assert isinstance(node, allowed_nodes), '{} not allowed'.format(type(node).__name__)


def get_children(root: ast.AST) -> List[ast.AST]:
    check_node_type(root)

    if isinstance(root, ast.Module):
        return root.body

    if isinstance(root, ast.BinOp):
        return [root.left, root.op, root.right]

    if isinstance(root, (ast.Num, ast.expr_context, Identifier, ast.operator)):
        return []

    if isinstance(root, ast.Name):
        return [Identifier(value=root.id), root.ctx]

    if isinstance(root, ast.Return):
        return [root.value] if root.value else []

    if isinstance(root, ast.Expr):
        return [root.value]

    if isinstance(root, ast.FunctionDef):
        return [Identifier(value=root.name), root.args, Body(values=root.body),
                DecoratorList(values=root.decorator_list)]

    if isinstance(root, ast.arguments):
        return root.args

    if isinstance(root, ast.arg):
        return [Identifier(value=root.arg)]

    if isinstance(root, ast.Call):
        return [root.func, CallArgs(values=root.args)]

    if isinstance(root, ast.Assign):
        return [Targets(values=root.targets), root.value]

    if isinstance(root, ast.ClassDef):
        children = [Identifier(value=root.name), ClassBases(values=root.bases),
                    Keywords(values=root.keywords), Body(values=root.body),
                    DecoratorList(values=root.decorator_list)]
        if root.starargs is not None:
            children.append(root.starargs)

        if root.kwargs is not None:
            children.append(root.kwargs)

        return children

    if isinstance(root, ast.keyword):
        return [Identifier(value=root.arg), root.value]

    if isinstance(root, ast.Delete):
        return root.targets

    if isinstance(root, ast.AugAssign):
        return [root.target, root.op, root.value]

    if isinstance(root, ListOfNodes):
        return root.values

    assert False


def get_children_pairs(left_tree: Tree, right_tree: Tree) -> Iterable[Tuple[Tree, Tree]]:
    return zip(left_tree.children, right_tree.children)


def match_two_ast_nodes(left: ast.AST, right: ast.AST) -> bool:
    if type(left) != type(right):
        return False

    if isinstance(left, Identifier):
        return left.value == right.value

    if isinstance(left, ast.Num):
        assert isinstance(right, ast.Num)
        return left.n == right.n

    return True


def match_two_tree_nodes(left: Tree, right: Tree) -> bool:
    return match_two_ast_nodes(left.node, right.node)


def match_two_tree(left_tree: Tree, right_tree: Tree, res=None):
    if res is None:
        res = {}

    cached_value = res.get((left_tree, right_tree))
    if cached_value is not None:
        return cached_value[0], cached_value[1], res

    roots_matches = int(match_two_tree_nodes(left_tree, right_tree))
    n_nodes = roots_matches
    kind = MatchKind.ROOT_ROOT
    ind = roots_matches
    for l, r in get_children_pairs(left_tree, right_tree):
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
            for child in left_tree.children[len(right_tree.children):]:
                patches.append(PatchDeleteSubtree(root=child))

        if len(right_tree.children) > len(left_tree.children):
            for child in right_tree.children[len(left_tree.children):]:
                patches.append(PatchInsertUnder(node=left_tree,
                                                inserted_tree=child))

        if ind == 0:
            patches.append(PatchEdit(node_from=left_tree, node_to=right_tree))

        for l, r in zip(left_tree.children, right_tree.children):
            patches.extend(get_patches(l, r, res))

        return patches
    elif kind == MatchKind.ROOT_CHILD:
        patches.append(PatchInsertAbove(node=left_tree,
                                        inserted_tree=right_tree,
                                        new_child_position=ind))
        patches.extend(get_patches(left_tree, right_tree.children[ind], res))
        return patches
    elif kind == MatchKind.CHILD_ROOT:
        for i, child in enumerate(left_tree.children):
            if i != ind:
                patches.append(PatchDeleteSubtree(root=child))
        patches.append(PatchDeleteNode(node=left_tree))
        patches.extend(get_patches(left_tree.children[ind], right_tree, res))
        return patches

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


def preorder(root: Tree, res: List[Tree] = None) -> List[Tree]:
    res = res or []
    res.append(root)
    for c in root.children:
        preorder(c, res)
    return res


def ast2tree(root: ast.AST) -> Tree:
    def _ast2tree(r: ast.AST) -> Tree:
        check_node_type(r)
        tr = Tree(r)
        for child in get_children(r):
            tr.add_child(_ast2tree(child))
        return tr

    tree = _ast2tree(root)
    for i, node in enumerate(preorder(tree)):
        node.set_pk(i)

    return tree


def get_description_of_changes(left_code: str, right_code: str) -> List[str]:
    left_ast = ast.parse(left_code)
    right_ast = ast.parse(right_code)

    logger.debug('\n%s\n%s', left_code, ast.dump(left_ast))
    logger.debug('\n%s\n%s', right_code, ast.dump(right_ast))

    left_tree = ast2tree(left_ast)
    right_tree = ast2tree(right_ast)

    logger.debug('\n%s', pretty_print_tree(left_tree))
    logger.debug('\n%s', pretty_print_tree(right_tree))

    num, _, result = match_two_tree(left_tree, right_tree)

    patches = get_patches(left_tree, right_tree, result)

    return list(map(lambda patch: patch.get_description(), patches))
