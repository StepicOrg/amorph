import logging
import unittest
import textwrap

from amorph.diff import get_patches
from amorph.diff.models import *

logging.disable(logging.DEBUG)


class TestPatches(unittest.TestCase):
    def test_linepatch(self):
        left_code = textwrap.dedent('''
                    def f(a, b):
                        return a + b
                    ''')
        right_code = textwrap.dedent('''
                    def f(a, b):
                        return a + b + 5
                    ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], LinePatch)

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
                        for i in range(b):
                            print(a)
                        return a + b
                    ''')
        right_code = textwrap.dedent('''
                    def f(a, b):
                        f = open('output.txt', 'r')
                        f.write(a * b)
                        f.close()
                        return a + b
                    ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 1)
        self.assertIsInstance(list_of_changes[0], ReplacePatch)

if __name__ == '__main__':
    unittest.main()
