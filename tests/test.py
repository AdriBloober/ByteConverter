import unittest
from byte_converter import read_bytes, to_bytes


class ClassToBytesTest(unittest.TestCase):
    def test_bool(self):
        for o in [True, False]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_int(self):
        for o in [1, -1213, 12412, 142421, 121251251, 12, 0, 114212412412]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_string(self):
        for o in ["a", "", "Hello World!"]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_float(self):
        for o in [1.0, 14114.1413413, 141.141441, 1414141414.12131414, -11414.14]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_list(self):
        for o in [[1, 14], ["asdf", 123], ["12", 113.0, [13, 12], 1000913.1]]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_class(self):
        class B:
            def __init__(self, value):
                self.value = round(value)

            @property
            def abs_value(self):
                return 0 - self.value

        class A:
            def __init__(self, v):
                if isinstance(v, B):
                    self.v = v
                else:
                    self.v = B(v)

            def __eq__(self, other):
                if isinstance(other, B):
                    return other == self.v
                elif isinstance(other, A):
                    return self.__eq__(self.v)

        for o in [A(13.12), A(24), A(2414.14), [A(123 + 13.1), A(-13.1)]]:
            self.assertEqual(read_bytes(to_bytes(o), parsable_classes=[A, B]), o)

    def test_dict(self):
        for o in [{"a": 12, "b": 133}, {"a": {"b": 1, "c": [1, 13.1]}, "b": 13}]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_none(self):
        for o in [None, {"a": None}]:
            self.assertEqual(read_bytes(to_bytes(o)), o)

    def test_object_ignored(self):
        class C:
            bc_ignore_attributes = ["b"]
            a = 12
            b = 1441

        a = C()
        a.b = 131
        t_b = read_bytes(to_bytes(a), parsable_classes=C)
        self.assertEqual(t_b.a, a.a)
        self.assertEqual(t_b.b, C.b)

    def test_object_whitelisted(self):
        class D:
            bc_whitelisted_attributes = ["a"]
            a = 1
            b = 2
            c = 3

        d = D()
        d.b = 1313
        d.c = 1314
        t_b = read_bytes(to_bytes(d), parsable_classes=D)
        self.assertEqual(t_b.a, d.a)
        self.assertEqual(t_b.b, D.b)
        self.assertEqual(t_b.c, D.c)


if __name__ == "__main__":
    unittest.main()
