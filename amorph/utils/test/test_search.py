import logging
import unittest

from amorph.utils import find_closest
from amorph.metric import string_similarity

logging.disable(logging.DEBUG)


class TestSearch(unittest.TestCase):
    def test_find_closest(self):
        source = 'a + b + c'
        samples = ['a + b', '(a + b) * c', 'a + b * c']
        sample = find_closest(source, samples, string_similarity)

        self.assertEqual(sample, samples[2])

if __name__ == '__main__':
    unittest.main()
