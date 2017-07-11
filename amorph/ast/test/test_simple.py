import logging
import unittest

from amorph.ast import get_description_of_changes

logging.disable(logging.DEBUG)


class TestSimple(unittest.TestCase):
    def test_simple(self):
        left_code = 'a + b'
        right_code = '(a + b) * c'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)


if __name__ == '__main__':
    unittest.main()
