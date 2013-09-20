# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import dis
import unittest

from pykit.analysis import cfa
from pykit.ir.interp import UncaughtException

from numba2.functionwrapper import FunctionWrapper
from numba2.frontend import translate, interpret
from numba2 import environment

function = lambda f: FunctionWrapper(f, None)

#===------------------------------------------------------------------===
# Helpers
#===------------------------------------------------------------------===

def run(f, expected, args, ssa=True):
    env = environment.fresh_env()
    code = translate(f, env)
    if ssa:
        cfa.run(code)
    result = interpret(code, args=args)
    assert result == expected, "Got %s, expected %s" % (result, expected)

#===------------------------------------------------------------------===
# Tests
#===------------------------------------------------------------------===

class TestBytecodeTranslation(unittest.TestCase):

    #===------------------------------------------------------------------===
    # Ops
    #===------------------------------------------------------------------===

    def test_compare(self):
        def f(a, b):
            return a < b
        run(f, True, [5, 6])

    def test_binop(self):
        def f(a, b):
            return a + b
        run(f, 11, [5, 6])

    #===------------------------------------------------------------------===
    # Calls
    #===------------------------------------------------------------------===

    def test_call(self):
        @function
        def f(a, b):
            return g(a + b)

        @function
        def g(x):
            return x * x

        run(f.py_func, 100, [4, 6])

    def test_recursion(self):
        @function
        def fact(n):
            if n > 1:
                return n * fact(n - 1)
            return 1

        run(fact.py_func, 120, [5])

    #===------------------------------------------------------------------===
    # Control Flow
    #===------------------------------------------------------------------===

    def test_while(self):
        def f(a, b):
            while a < b:
                a = a + 1
            return a + b

        # print(translate(f))
        run(f, 20, [0, 10])

    def test_for(self):
        def f(a, b):
            sum = 0
            for i in range(a, b):
                sum += i
            return sum

        # dis.dis(f)
        # print(translate(f))
        run(f, 45, [0, 10])

    #===------------------------------------------------------------------===
    # Exceptions
    #===------------------------------------------------------------------===

    def test_raise(self):
        def f(a, b):
            sum = 0
            for i in range(a, b):
                sum += i
                if i >= 5:
                    raise ValueError(sum)
            return sum

        # dis.dis(f)
        # print(translate(f))
        try:
            run(f, 15, [0, 10], ssa=False) # TODO: exc_throw
        except UncaughtException, e:
            exc = e.args[0]
            assert isinstance(exc, ValueError)
            self.assertEqual(exc.args[0], 15)
        else:
            raise Exception("Expected 'UncaughtException'")

    def test_catch_noerror(self):
        def f(a, b):
            try:
                a + b
            except ValueError:
                return 1
            except Exception:
                return 2
            else:
                return 3

        # dis.dis(f)
        # print(translate(f))
        run(f, 3, [0, 10])

    def test_catch_error(self):
        def f(a, b):
            try:
                raise ValueError(a)
            except ValueError:
                return 1
            except Exception:
                return 2
            else:
                return 3

        # dis.dis(f)
        # print(translate(f))
        run(f, 1, [0, 10], ssa=False) # TODO: exc_throw


if __name__ == '__main__':
    # TestBytecodeTranslation('test_recursion').debug()
    unittest.main()