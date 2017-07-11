import logging
import unittest

from amorph.ast import get_description_of_changes

logging.disable(logging.DEBUG)


class TestPatchesStructure(unittest.TestCase):
    def test_delete_patches_structure(self):
        left_code = 'def f():' \
                    '  a + b'
        right_code = 'a + b'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertEqual(len(list_of_changes), 2)

    def test_insert_patches_structure(self):
        left_code = 'a + b'
        right_code = 'def f():' \
                     '  a + b'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertEqual(len(list_of_changes), 2)


if __name__ == '__main__':
    unittest.main()
