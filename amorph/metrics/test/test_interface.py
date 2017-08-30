import unittest
from operator import itemgetter

from amorph.metrics import string_similarity


class TestInterface(unittest.TestCase):
    def test_key(self):
        dict_src = {'field': 'a + b + c'}
        dict_near = {'field': 'a + b * c'}
        dict_far = {'field': '(a + b) * c'}

        metric1 = string_similarity(dict_src, dict_near, itemgetter('field'))
        metric2 = string_similarity(dict_src, dict_far, itemgetter('field'))

        self.assertGreater(metric1, metric2)

if __name__ == '__main__':
    unittest.main()
