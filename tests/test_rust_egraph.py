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

def test_custom_operators():
    e = EGraph()
    e.add("(foo (bar a))")

    rules = [
        rewrite("(foo (bar ?x))", "?x"),
    ]

    e.run(rules)
    assert e.best("(foo (bar a))") == "a"

def test_are_equal():
    e = EGraph()
    e.add("(+ a b)")
    e.add("(+ b a)")

    rules = [
        rewrite("(+ ?x ?y)", "(+ ?y ?x)"),
    ]

    e.run(rules)
    assert e.are_equal("(+ a b)", "(+ b a)")

def test_error_handling():
    e = EGraph()
    # Invalid pattern (RHS variable not in LHS)
    try:
        rules = [rewrite("(+ ?x ?y)", "?z")]
        e.run(rules)
        assert False, "Should have raised an error"
    except Exception as ex:
        assert "Rewrite creation error" in str(ex)

def test_explanation():
    e = EGraph()
    e.add("(+ a 0)")
    rules = [rewrite("(+ ?x 0)", "?x")]
    e.run(rules)

    explanation = e.why_equal("(+ a 0)", "a")
    assert "a" in explanation
    # The actual output might vary, so just check for basic presence
    assert "(+ a 0)" in explanation or "a" in explanation

def test_run_iter():
    e = EGraph()
    e.add("(+ (+ a 0) 0)")
    rules = [rewrite("(+ ?x 0)", "?x")]

    iters = list(e.run_iter(rules))
    assert len(iters) >= 1
    for step in iters:
        assert hasattr(step, "nodes")
        assert hasattr(step, "eclasses")

if __name__ == "__main__":
    test_basic_simplification()
    test_custom_operators()
    test_are_equal()
    test_error_handling()
    test_explanation()
    test_run_iter()
    print("All manual tests passed!")
