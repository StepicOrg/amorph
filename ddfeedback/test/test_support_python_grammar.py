import logging
import textwrap
import unittest

from ddfeedback import get_description_of_changes

logging.disable(logging.DEBUG)


class TestSupportPythonGrammar(unittest.TestCase):
    def test_literals(self):
        left_code = textwrap.dedent('''
                                    5
                                    42.1
                                    5j + 1
                                    "42"
                                    [1, 2, 3]
                                    {1, 3, 4}
                                    {1: 2, 3: 4}
                                    True
                                    None
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_variables(self):
        left_code = textwrap.dedent('''
                                    a
                                    a = 1
                                    del a
                                    a, *b = it
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_operations(self):
        left_code = textwrap.dedent('''
                                    -a
                                    +a
                                    not a
                                    ~a
                                    a or b
                                    a and b
                                    a + b
                                    a - b
                                    a * b
                                    a / b
                                    a // b
                                    a % b
                                    a ** b
                                    a << b
                                    a >> b
                                    a & b
                                    a ^ b
                                    a | b
                                    a < b
                                    a < b < c
                                    a in b
                                    a is b
                                    a == b
                                    a != b
                                    a if b else c
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_call(self):
        left_code = textwrap.dedent('''
                                    f(x)
                                    func(a, b=c, *d, **e)
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_attribute(self):
        left_code = 'a.b'
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_subscript(self):
        left_code = textwrap.dedent('''
                                    a[1]
                                    a[1:2]
                                    a[1:2, 3]
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_comprehensions(self):
        left_code = textwrap.dedent('''
                                    [x for x in a]
                                    [c for line in file for c in line]
                                    (n**2 for n in it if n > 5 if n < 10)
                                    {l: r for (l, r) in it}
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_statements(self):
        left_code = textwrap.dedent('''
                                    a = 1
                                    a = b = 1
                                    a, b = c
                                    a += 1
                                    raise a
                                    assert a
                                    del a
                                    pass
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_imports(self):
        left_code = textwrap.dedent('''
                                    import a
                                    from a import b
                                    from ..foo.bar import a as b, c
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_control_flow(self):
        left_code = textwrap.dedent('''
                                    if a:
                                        a += 2

                                    for a in b:
                                        a += 2
                                        if a:
                                            continue

                                    while a < b:
                                        a += 2
                                        break

                                    try:
                                        a + 2
                                    except TypeError:
                                        pass

                                    try:
                                        b + 2
                                    except TypeError:
                                        pass
                                    finally:
                                        pass

                                    with a as b, c as d:
                                        b + d

                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_func_def(self):
        left_code = textwrap.dedent('''
                                    def f():
                                        pass

                                    def f(a):
                                        a + 2

                                    def f(a):
                                        return a + 2

                                    @dec1
                                    @dec2
                                    def f(a, b=1, c=2, *d, e, x=3, **g):
                                        global y
                                        nonlocal z
                                        yield a
                                        yield from a
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

    def test_class_def(self):
        left_code = textwrap.dedent('''
                                    class A(B, C, z=D):
                                        pass
                                    ''')
        right_code = '42'
        list_of_changes = get_description_of_changes(left_code, right_code)
        self.assertGreater(len(list_of_changes), 0)

if __name__ == '__main__':
    unittest.main()
