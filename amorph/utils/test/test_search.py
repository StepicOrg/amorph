import unittest

import time

from amorph.metrics import string_similarity
from amorph.utils import find_closest


class TestSearch(unittest.TestCase):
    def test_find_closest(self):
        source = 'a + b + c'
        samples = ['a + b', '(a + b) * c', 'a + b * c']
        sample = find_closest(source, samples, string_similarity)

        self.assertEqual(sample, samples[2])

    def test_find_closest_timeout(self):
        source = 'a + b + c'
        samples = ['a + b + c + d + e + f'] * 50000
        samples.append('a + b * c')

        timeout = 0.05
        start_time = time.time()
        find_closest(source, samples, string_similarity, timeout=timeout)
        real_time = time.time() - start_time
        self.assertAlmostEqual(real_time, timeout, delta=timeout * 0.1)


if __name__ == '__main__':
    unittest.main()
