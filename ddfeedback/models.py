import ast
from typing import List

from .constants import PatchKind


class Identifier(ast.AST):
    value: str


class ListOfNodes(ast.AST):
    values: list


class Body(ListOfNodes):
    pass


class DecoratorList(ListOfNodes):
    pass


class ClassBases(ListOfNodes):
    pass


class Keywords(ListOfNodes):
    pass


class CallArgs(ListOfNodes):
    pass


class Targets(ListOfNodes):
    pass


class Tree(object):
    def __init__(self, node: ast.AST, pk: int = None, parent=None, children=None):
        self.node: ast.AST = node
        self.pk: int = pk
        self.name: str = self.get_name_by_node_and_pk(node, pk)
        self.parent: Tree = parent
        self.children: List[Tree] = children or []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def set_pk(self, pk):
        self.pk = pk
        self.name = self.get_name_by_node_and_pk(self.node, self.pk)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __str__(self):
        return '{}{}'.format(self.name,
                             ': [{}]'.format(', '.join(map(str, self.children)))
                             if not self.is_leaf() else '')

    @staticmethod
    def get_name_by_node_and_pk(node: ast.AST, pk: int) -> str:
        if isinstance(node, Identifier):
            s = f'ID: {node.value}'
        elif isinstance(node, ast.Num):
            s = f'Num: {node.n}'
        else:
            s = type(node).__name__
        return f'{pk}_{s}' if pk is not None else s


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

    def __init__(self, node: Tree, inserted_tree: Tree):
        self.node = node
        self.inserted_tree = inserted_tree

    def get_description(self) -> str:
        return f'insert tree="{self.inserted_tree}" under node="{self.node.name}"'


class PatchInsertAbove(Patch):
    kind: PatchKind = PatchKind.INSERT_ABOVE
    node: Tree
    inserted_tree: Tree
    new_child_position: int

    def __init__(self, node: Tree, inserted_tree: Tree, new_child_position: int):
        self.node = node
        self.inserted_tree = inserted_tree
        self.new_child_position = new_child_position

    def get_description(self) -> str:
        child = self.inserted_tree.children[self.new_child_position]
        self.inserted_tree.children[self.new_child_position] = 'Place_for_child_node'
        inserted_tree = str(self.inserted_tree)
        self.inserted_tree.children[self.new_child_position] = child
        return f'insert tree="{inserted_tree}" ' \
               f'above node="{self.node.name}" ' \
               f'new_child_position={self.new_child_position}'


class PatchDeleteNode(Patch):
    kind: PatchKind = PatchKind.DELETE_NODE
    node: Tree

    def __init__(self, node: Tree):
        self.node = node

    def get_description(self) -> str:
        return f'delete node "{self.node.name}"'


class PatchDeleteSubtree(Patch):
    kind: PatchKind = PatchKind.DELETE_SUBTREE
    root: Tree

    def __init__(self, root: Tree):
        self.root = root

    def get_description(self) -> str:
        return f'delete subtree with root="{self.root.name}"'
