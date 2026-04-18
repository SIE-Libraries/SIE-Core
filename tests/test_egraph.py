import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sie_core import EGraph, ENode, Pattern, Rewrite, Runner

def test_simple_identity():
    # x + 0 == x
    eg = EGraph()
    x = eg.add(ENode("x", ()))
    zero = eg.add(ENode("0", ()))
    expr = eg.add(ENode("+", (x, zero)))

    lhs = Pattern(("+", (Pattern("?a"), Pattern("0"))))
    rhs = Pattern("?a")
    rule = Rewrite("add-zero", lhs, rhs)

    runner = Runner(eg)
    runner.run([rule])

    assert eg.find(expr) == eg.find(x)
    print("test_simple_identity passed!")

def test_mul_div():
    # (a * 2) / 2 == a
    eg = EGraph()
    a = eg.add(ENode("a", ()))
    two = eg.add(ENode("2", ()))
    mul = eg.add(ENode("*", (a, two)))
    div = eg.add(ENode("/", (mul, two)))

    lhs = Pattern(("/", (Pattern(("*", (Pattern("?x"), Pattern("?y")))), Pattern("?y"))))
    rhs = Pattern("?x")
    rule = Rewrite("div-mul", lhs, rhs)

    runner = Runner(eg)
    runner.run([rule])

    assert eg.find(div) == eg.find(a)
    print("test_mul_div passed!")

def test_transitivity():
    # a == b, b == c => a == c
    eg = EGraph()
    a = eg.add(ENode("a", ()))
    b = eg.add(ENode("b", ()))
    c = eg.add(ENode("c", ()))

    eg.union(a, b)
    eg.union(b, c)
    eg.rebuild()

    assert eg.find(a) == eg.find(c)
    print("test_transitivity passed!")

if __name__ == "__main__":
    test_simple_identity()
    test_mul_div()
    test_transitivity()
