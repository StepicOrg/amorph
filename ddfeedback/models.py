import ast
from typing import List

from .constants import PatchKind


class Identifier(ast.AST):
    value: str


class IntValue(ast.AST):
    value: int


class ListOfNodes(ast.AST):
    values: List[ast.AST]
    name: str


class Tree(object):
    def __init__(self, node: ast.AST, pk: int = None, parent=None, children=None):
        self.node: ast.AST = node
        self.pk: int = pk
        self.parent: Tree = parent
        self.children: List[Tree] = children or []

    @property
    def name(self) -> str:
        if isinstance(self.node, Identifier):
            s = f'ID: {self.node.value}'
        elif isinstance(self.node, ast.Num):
            s = f'Num: {self.node.n}'
        elif isinstance(self.node, ListOfNodes):
            s = self.node.name
        else:
            s = type(self.node).__name__
        return f'{self.pk}_{s}' if self.pk is not None else s

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __str__(self):
        return '{}{}'.format(self.name,
                             ': [{}]'.format(', '.join(map(str, self.children)))
                             if not self.is_leaf() else '')


class Patch(object):
    kind: PatchKind

    def get_description(self) -> str:
        raise NotImplementedError


class PatchEdit(Patch):
    kind: PatchKind = PatchKind.EDIT
    node_from: Tree
    node_to: Tree

    def __init__(self, node_from: Tree, node_to: Tree):
        self.node_from = node_from
        self.node_to = node_to

    def get_description(self) -> str:
        return f'change "{self.node_from.name}" to "{self.node_to.name}"'


class PatchInsertUnder(Patch):
    kind: PatchKind = PatchKind.INSERT_UNDER
    node: Tree
    inserted_tree: Tree

    def __init__(self, node: Tree, inserted_trees: List[Tree]):
        self.node = node
        self.inserted_trees = inserted_trees

    def get_description(self) -> str:
        return f'insert tree="{self.inserted_trees}" under node="{self.node.name}"'


class PatchInsertAbove(Patch):
    kind: PatchKind = PatchKind.INSERT_ABOVE
    node: Tree
    inserted_tree: Tree
    new_child_position: List[int]

    def __init__(self, node: Tree, inserted_tree: Tree, new_child_position: List[int]):
        self.node = node
        self.inserted_tree = inserted_tree
        self.new_child_position = new_child_position

    def get_description(self) -> str:
        child = self.inserted_tree.children[self.new_child_position[0]]
        for pos in self.new_child_position[1:]:
            child = child.children[pos]
        child.parent.children[self.new_child_position[-1]] = 'Place_for_child_node'
        inserted_tree = str(self.inserted_tree)
        child.parent.children[self.new_child_position[-1]] = child
        return f'insert tree="{inserted_tree}" ' \
               f'above node="{self.node.name}" ' \
               f'new_child_position={self.new_child_position}'


class PatchDelete(Patch):
    kind: PatchKind = PatchKind.DELETE
    tree: Tree
    delete_root: bool
    not_deleted_descendants: List[int]

    def __init__(self, tree: Tree, delete_root: bool, not_deleted_descendants: List[int]):
        self.tree = tree
        self.delete_root = delete_root
        self.not_deleted_descendants = not_deleted_descendants

    def get_description(self) -> str:
        return f'delete tree "{self.tree.name}"; ' \
               f'delete_root = {self.delete_root}; ' \
               f'not_deleted_descendants = {self.not_deleted_descendants};'
