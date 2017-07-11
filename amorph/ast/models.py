import ast
import astunparse
from typing import List
import uuid

from .constants import PatchKind


class Tree(object):
    def __init__(self, node: ast.AST, parent=None):
        self.node: ast.AST = node
        self.parent: Tree = parent

        self.pk: str = str(uuid.uuid4())
        self.name = f'{type(self.node).__name__} #{self.pk}'

        self.children: List[Tree] = []
        self.size = 1
        for child in ast.iter_child_nodes(self.node):
            self.children.append(Tree(child, self))
            self.size += self.children[-1].size

    def __str__(self):
        children_desc = ', '.join(map(str, self.children))
        return f'{self.name}: [{children_desc}]'

    def to_code(self):
        return astunparse.unparse(self.node)


class Patch(object):
    kind: PatchKind

    def get_description(self) -> str:
        raise NotImplementedError

    def get_weight(self) -> int:
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

    def get_weight(self) -> int:
        return 1


class PatchInsertUnder(Patch):
    kind: PatchKind = PatchKind.INSERT_UNDER
    node: Tree
    inserted_trees: Tree

    def __init__(self, node: Tree, inserted_trees: List[Tree]):
        self.node = node
        self.inserted_trees = inserted_trees

    def get_description(self) -> str:
        return f'insert tree="{self.inserted_trees}" under node="{self.node.name}"'

    def get_weight(self) -> int:
        weight = 0
        for tree in self.inserted_trees:
            weight += tree.size
        return weight


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

    def get_weight(self) -> int:
        from .utils import get_child_by_path
        all_nodes = self.inserted_tree.size
        child = get_child_by_path(self.inserted_tree, self.new_child_position)
        if child is not None:
            return all_nodes - child.size
        return all_nodes


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

    def get_weight(self) -> int:
        from .utils import get_child_by_path

        if self.delete_root:
            all_nodes = self.tree.size
            child = get_child_by_path(self.tree, self.not_deleted_descendants)
            if child is not None:
                return all_nodes - child.size
            return all_nodes

        else:
            deleted_nodes = 0
            not_deleted = set(self.not_deleted_descendants)
            for i, child in enumerate(self.tree.children):
                if i not in not_deleted:
                    deleted_nodes += child.size
            return deleted_nodes
