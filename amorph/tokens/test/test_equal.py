import logging
import textwrap
import unittest

from amorph.tokens import get_patches

logging.disable(logging.DEBUG)


class TestEqual(unittest.TestCase):
    def test_equal(self):
        left_code = 'a + b'
        right_code = textwrap.dedent('''
                     # some comment
                     a  +   b
                     ''')
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertEqual(len(list_of_changes), 0)

    def test_nonequal(self):
        left_code = 'a + b'
        right_code = '(a + b) * c'
        list_of_changes = list(get_patches(left_code, right_code))

        self.assertGreater(len(list_of_changes), 0)

if __name__ == '__main__':
    unittest.main()
