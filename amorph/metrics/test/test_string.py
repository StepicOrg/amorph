import logging
import unittest

from amorph.metrics import string_similarity

logging.disable(logging.DEBUG)


class TestString(unittest.TestCase):
    def test_string_similarity(self):
        source = 'a + b + c'

        sample1 = 'a + b * c'
        metric1 = string_similarity(source, sample1)

        sample2 = '(a + b) * c'
        metric2 = string_similarity(source, sample2)

        self.assertGreater(metric1, metric2)

if __name__ == '__main__':
    unittest.main()
