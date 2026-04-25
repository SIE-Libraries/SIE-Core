from sie_core import EGraph, rewrite
import pytest

def test_basic_simplification():
    e = EGraph()
    e.add("(+ a 0)")

    rules = [
        rewrite("(+ ?x 0)", "?x"),
    ]

    e.run(rules)
    assert e.best("(+ a 0)") == "a"

def test_cost_functions():
    e = EGraph()
    e.add("(+ a (+ b 0))")
    rules = [rewrite("(+ ?x 0)", "?x")]
    e.run(rules)

    best_size = e.extract("(+ a (+ b 0))", cost="size")
    best_depth = e.extract("(+ a (+ b 0))", cost="depth")
    assert best_size == "(+ a b)"
    assert best_depth == "(+ a b)"

def test_why_equal_checks():
    e = EGraph()
    e.add("a")
    e.add("b")

    # Not equal check
    try:
        e.why_equal("a", "b")
        assert False, "Should have raised error for non-equivalence"
    except Exception as ex:
        assert "are not equal" in str(ex)

    # Not in graph check
    try:
        e.why_equal("a", "c")
        assert False, "Should have raised error for 'c'"
    except Exception as ex:
        assert "not found in e-graph" in str(ex)

def test_are_equal():
    e = EGraph()
    e.add("(+ a b)")
    e.add("(+ b a)")

    rules = [
        rewrite("(+ ?x ?y)", "(+ ?y ?x)"),
    ]

    e.run(rules)
    assert e.are_equal("(+ a b)", "(+ b a)")

if __name__ == "__main__":
    test_basic_simplification()
    test_cost_functions()
    test_why_equal_checks()
    test_are_equal()
    print("All manual tests passed!")
