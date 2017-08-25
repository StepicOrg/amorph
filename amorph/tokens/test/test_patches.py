import logging
import unittest
import textwrap

from amorph.tokens import get_patches
from amorph.models import DeletePatch, InsertPatch, ReplacePatch

logging.disable(logging.DEBUG)


class TestPatches(unittest.TestCase):
    def test_deletepatch(self):
        left_code = textwrap.dedent('''
                    def f(a, b):
                        if a + 1 == b:
                            return 2 * a - b
                        return a + b
                    ''')
        right_code = textwrap.dedent('''
                    def f(a, b):
                        return a + b
                    ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], DeletePatch)

    def test_insertpatch(self):
        left_code = textwrap.dedent('''
                    def f(a, b):
                        return a + b
                    ''')
        right_code = textwrap.dedent('''
                    def f(a, b):
                        if a + 1 == b:
                            return 2 * a - b
                        return a + b
                    ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], InsertPatch)

    def test_replacepatch(self):
        left_code = textwrap.dedent('''
                    def f(a, b):
                        return a + b
                    ''')
        right_code = textwrap.dedent('''
                    def f(a, b):
                        return a   *  b
                    ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], ReplacePatch)

    def test_append_index(self):
        left_code = 'print("Hello World")'
        right_code = 'print("Hello World");'
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        patch = list_of_changes[0]
        self.assertIsInstance(patch, InsertPatch)
        self.assertEqual(patch.pos, len(left_code))

if __name__ == '__main__':
    unittest.main()
