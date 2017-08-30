import unittest
from operator import itemgetter

from amorph.utils import find_closest
from amorph.metrics import string_similarity


class TestInterface(unittest.TestCase):
    def test_key(self):
        source = {'field': 'a + b + c'}
        samples = [{'field': 'a + b'},
                   {'field': '(a + b) * c'},
                   {'field': 'a + b * c'}]
        sample = find_closest(source, samples, string_similarity, key=itemgetter('field'))

        self.assertEqual(sample, samples[2])

if __name__ == '__main__':
    unittest.main()
