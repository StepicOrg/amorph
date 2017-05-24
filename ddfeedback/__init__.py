import ast
import logging
from typing import List

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(name)s %(asctime)s %(levelname)s %(message)s')


def get_description_of_changes(left_code: str, right_code: str) -> List[str]:
    from .utils import ast2tree, pretty_print_tree, match_two_tree, get_patches
    left_ast = ast.parse(left_code)
    right_ast = ast.parse(right_code)

    _logger.info('\n%s\n%s', left_code, ast.dump(left_ast))
    _logger.info('\n%s\n%s', right_code, ast.dump(right_ast))

    left_tree = ast2tree(left_ast)
    right_tree = ast2tree(right_ast)

    _logger.info('\n%s', pretty_print_tree(left_tree))
    _logger.info('\n%s', pretty_print_tree(right_tree))

    num, _, result = match_two_tree(left_tree, right_tree)

    patches = get_patches(left_tree, right_tree, result)

    return list(map(lambda patch: patch.get_description(), patches))
