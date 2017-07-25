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
        print([str(patch) for patch in list_of_changes])

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], ReplacePatch)

if __name__ == '__main__':
    unittest.main()
