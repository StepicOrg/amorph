import ast
import logging
from typing import List, Iterable, Tuple

from .constants import MatchKind
from .models import (Identifier, ListOfNodes, Tree, PatchDelete,
                     PatchInsertAbove, PatchEdit, PatchInsertUnder, Patch, IntValue)

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
                 ast.For,
                 ast.While,
                 ast.If,
                 ast.withitem,
                 ast.With,
                 ast.Raise,
                 ast.excepthandler,
                 ast.Try,
                 ast.Assert,
                 ast.alias,
                 ast.Import,
                 ast.ImportFrom,
                 ast.Global,
                 ast.Nonlocal,
                 ast.Pass,
                 ast.Break,
                 ast.Continue,
                 ast.BoolOp,
                 ast.boolop,
                 ast.UnaryOp,
                 ast.unaryop,
                 ast.Lambda,
                 ast.IfExp,
                 ast.Dict,
                 ast.Set,
                 ast.comprehension,
                 ast.ListComp,
                 ast.SetComp,
                 ast.GeneratorExp,
                 ast.DictComp,
                 ast.Yield,
                 ast.YieldFrom,
                 ast.cmpop,
                 ast.Compare,
                 ast.Ellipsis,
                 ast.Str,
                 ast.Bytes,
                 ast.NameConstant,
                 ast.Attribute,
                 ast.Subscript,
                 ast.Slice,
                 ast.ExtSlice,
                 ast.Index,
                 ast.Starred,
                 ast.List,
                 ast.Tuple,
                 type(None),
                 Identifier,
                 IntValue,
                 ListOfNodes)


def check_node_type(node):
    assert isinstance(node, allowed_nodes), '{} not allowed'.format(type(node).__name__)


def filter_empty(*args):
    def f(item):
        if item is None:
            return False

        if isinstance(item, (Identifier, IntValue)):
            return item.value is not None

        if isinstance(item, ListOfNodes):
            return bool(item.values)

        return True

    return list(filter(f, args))


def get_children(root: ast.AST) -> List[ast.AST]:
    check_node_type(root)

    if isinstance(root, ast.Module):
        return root.body

    if isinstance(root, ast.BinOp):
        return [root.left, root.op, root.right]

    if isinstance(root, (ast.Num, ast.expr_context, Identifier, IntValue, ast.operator,
                         ast.Pass, ast.Break, ast.Continue, ast.boolop, ast.unaryop,
                         ast.cmpop, ast.Str, ast.Bytes, ast.NameConstant, ast.Ellipsis,
                         type(None))):
        return []

    if isinstance(root, ast.Name):
        return [Identifier(value=root.id), root.ctx]

    if isinstance(root, ast.Return):
        return filter_empty(root.value)

    if isinstance(root, ast.Expr):
        return [root.value]

    if isinstance(root, ast.FunctionDef):
        return filter_empty(Identifier(value=root.name),
                            root.args,
                            ListOfNodes(values=root.body, name='Body'),
                            ListOfNodes(values=root.decorator_list, name='DecoratorList'))

    if isinstance(root, ast.arguments):
        return filter_empty(ListOfNodes(values=root.args, name='Args'),
                            root.vararg,
                            ListOfNodes(values=root.kwonlyargs, name='Kwonlyargs'),
                            ListOfNodes(values=root.kw_defaults, name='Kw_defaults'),
                            root.kwarg,
                            ListOfNodes(values=root.defaults, name='Defaults'))

    if isinstance(root, ast.arg):
        return filter_empty(Identifier(value=root.arg), root.annotation)

    if isinstance(root, ast.Call):
        return filter_empty(root.func,
                            ListOfNodes(values=root.args, name='CallArgs'),
                            ListOfNodes(values=root.keywords, name='Keywords'))

    if isinstance(root, ast.Assign):
        return [ListOfNodes(values=root.targets, name='Targets'), root.value]

    if isinstance(root, ast.ClassDef):
        return filter_empty(Identifier(value=root.name),
                            ListOfNodes(values=root.bases, name='ClassBases'),
                            ListOfNodes(values=root.keywords, name='Keywords'),
                            ListOfNodes(values=root.body, name='Body'),
                            ListOfNodes(values=root.decorator_list, name='DecoratorList'))

    if isinstance(root, ast.keyword):
        return [Identifier(value=root.arg), root.value]

    if isinstance(root, ast.Delete):
        return root.targets

    if isinstance(root, ast.AugAssign):
        return [root.target, root.op, root.value]

    if isinstance(root, ast.For):
        return [root.target, root.iter,
                ListOfNodes(values=root.body, name='Body'),
                ListOfNodes(values=root.orelse, name='Else')]

    if isinstance(root, (ast.While, ast.If)):
        # noinspection PyUnresolvedReferences
        return [root.test,
                ListOfNodes(values=root.body, name='Body'),
                ListOfNodes(values=root.orelse, name='Else')]

    if isinstance(root, ast.withitem):
        return filter_empty(root.context_expr, root.optional_vars)

    if isinstance(root, ast.With):
        return [ListOfNodes(values=root.items, name='WithItems'),
                ListOfNodes(values=root.body, name='Body')]

    if isinstance(root, ast.Raise):
        return filter_empty(root.exc, root.cause)

    if isinstance(root, ast.excepthandler):
        return filter_empty(root.type,
                            Identifier(value=root.name),
                            ListOfNodes(values=root.body, name='Body'))

    if isinstance(root, ast.Try):
        return [ListOfNodes(values=root.body, name='Body'),
                ListOfNodes(values=root.handlers, name='Excepthandlers'),
                ListOfNodes(values=root.orelse, name='Else'),
                ListOfNodes(values=root.body, name='Body')]

    if isinstance(root, ast.Assert):
        return filter_empty(root.test, root.msg)

    if isinstance(root, ast.alias):
        return filter_empty(Identifier(value=root.name),
                            Identifier(value=root.asname))

    if isinstance(root, ast.Import):
        return root.names

    if isinstance(root, ast.ImportFrom):
        return filter_empty(Identifier(value=root.module),
                            ListOfNodes(values=root.names, name='Names'),
                            IntValue(value=root.level))

    if isinstance(root, (ast.Global, ast.Nonlocal)):
        # noinspection PyUnresolvedReferences
        return list(map(lambda name: Identifier(value=name), root.names))

    if isinstance(root, ast.BoolOp):
        return [root.op, ListOfNodes(values=root.values, name='Values')]

    if isinstance(root, ast.UnaryOp):
        return [root.op, root.operand]

    if isinstance(root, ast.Lambda):
        return [root.args, root.body]

    if isinstance(root, ast.IfExp):
        return [root.test, root.body, root.orelse]

    if isinstance(root, ast.Dict):
        return [ListOfNodes(values=root.keys, name='Keys'),
                ListOfNodes(values=root.values, name='Values')]

    if isinstance(root, ast.Set):
        return root.elts

    if isinstance(root, ast.comprehension):
        return [root.target, root.iter,
                ListOfNodes(values=root.ifs, name='Ifs')]

    if isinstance(root, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        # noinspection PyUnresolvedReferences
        return [root.elt,
                ListOfNodes(values=root.generators, name='Generators')]

    if isinstance(root, ast.DictComp):
        return [root.key, root.value,
                ListOfNodes(values=root.generators, name='Generators')]

    if isinstance(root, ast.Yield):
        return filter_empty(root.value)

    if isinstance(root, ast.YieldFrom):
        return [root.value]

    if isinstance(root, ast.Compare):
        return [root.left,
                ListOfNodes(values=root.ops, name='Ops'),
                ListOfNodes(values=root.comparators, name='Comparators')]

    if isinstance(root, ast.Attribute):
        return [root.value, Identifier(value=root.attr), root.ctx]

    if isinstance(root, ast.Slice):
        return filter_empty(root.lower, root.upper, root.step)

    if isinstance(root, ast.ExtSlice):
        return root.dims

    if isinstance(root, ast.Index):
        return [root.value]

    if isinstance(root, ast.Subscript):
        return [root.value, root.slice, root.ctx]

    if isinstance(root, ast.Starred):
        return [root.value, root.ctx]

    if isinstance(root, (ast.List, ast.Tuple)):
        # noinspection PyUnresolvedReferences
        return [ListOfNodes(values=root.elts, name='elts'), root.ctx]

    if isinstance(root, ListOfNodes):
        return root.values

    assert False, f'unknown type of node: {type(root)}'


def get_children_pairs(left_tree: Tree, right_tree: Tree) -> Iterable[Tuple[Tree, Tree]]:
    return zip(left_tree.children, right_tree.children)


def match_two_ast_nodes(left: ast.AST, right: ast.AST) -> bool:
    if type(left) != type(right):
        return False

    if isinstance(left, (Identifier, IntValue, ast.NameConstant)):
        return left.value == right.value

    if isinstance(left, ast.Num):
        return left.n == right.n

    if isinstance(left, (ast.Str, ast.Bytes)):
        # noinspection PyUnresolvedReferences
        return left.s == right.s

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
        node.pk = i

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

def is_descendant(descendant: Tree, ancestor: Tree) -> bool:
    while descendant is not None:
        if descendant in ancestor.children:
            return True
        descendant = descendant.parent
    return False
