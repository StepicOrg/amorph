import ast
import astunparse
import uuid

from .constants import PatchKind


class Tree(object):
    def __init__(self, node: ast.AST, parent=None):
        self.node = node
        self.parent = parent

        self.pk = str(uuid.uuid4())
        self.name = '{} #{}'.format(type(self.node).__name__, self.pk)

        self.children = []
        self.size = 1
        for child in ast.iter_child_nodes(self.node):
            self.children.append(Tree(child, self))
            self.size += self.children[-1].size

    def __str__(self):
        children_desc = ', '.join(map(str, self.children))
        return '{}: [{}]'.format(self.name, children_desc)

    def to_code(self):
        return astunparse.unparse(self.node)


class Patch(object):
    kind = PatchKind.UNDEFINED

    def get_description(self) -> str:
        raise NotImplementedError

    def get_weight(self) -> int:
        raise NotImplementedError


class PatchEdit(Patch):
    kind = PatchKind.EDIT

    def __init__(self, node_from: Tree, node_to: Tree):
        self.node_from = node_from
        self.node_to = node_to

    def get_description(self) -> str:
        return 'change "{}" to "{}"'.format(self.node_from.name, self.node_to.name)

    def get_weight(self) -> int:
        return 1


class PatchInsertUnder(Patch):
    kind = PatchKind.INSERT_UNDER

    def __init__(self, node: Tree, inserted_trees: list):
        self.node = node
        self.inserted_trees = inserted_trees

    def get_description(self) -> str:
        return 'insert tree="{}" under node="{}"'.format(self.inserted_trees, self.node.name)

    def get_weight(self) -> int:
        weight = 0
        for tree in self.inserted_trees:
            weight += tree.size
        return weight


class PatchInsertAbove(Patch):
    kind = PatchKind.INSERT_ABOVE

    def __init__(self, node: Tree, inserted_tree: Tree, new_child_position: list):
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
        return 'insert tree="{}" ' \
               'above node="{}" ' \
               'new_child_position={}'.format(inserted_tree,
                                              self.node.name,
                                              self.new_child_position)

    def get_weight(self) -> int:
        from .utils import get_child_by_path
        all_nodes = self.inserted_tree.size
        child = get_child_by_path(self.inserted_tree, self.new_child_position)
        if child is not None:
            return all_nodes - child.size
        return all_nodes


class PatchDelete(Patch):
    kind = PatchKind.DELETE

    def __init__(self, tree: Tree, delete_root: bool, not_deleted_descendants: list):
        self.tree = tree
        self.delete_root = delete_root
        self.not_deleted_descendants = not_deleted_descendants

    def get_description(self) -> str:
        return 'delete tree "{}"; ' \
               'delete_root = {}; ' \
               'not_deleted_descendants = {};'.format(self.tree.name,
                                                      self.delete_root,
                                                      self.not_deleted_descendants)

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
