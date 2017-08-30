import unittest

from amorph.metrics import string_similarity


class TestString(unittest.TestCase):
    def test_string_similarity(self):
        source = 'a + b + c'
        target_near = 'a + b * c'
        target_far = '(a + b) * c'

        metric1 = string_similarity(source, target_near)
        metric2 = string_similarity(source, target_far)

        self.assertGreater(metric1, metric2)


if __name__ == '__main__':
    unittest.main()
