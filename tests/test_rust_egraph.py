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

def test_introspection():
    e = EGraph()
    e.add("(+ a b)")

    ids = e.eclass_ids()
    assert len(ids) > 0

    expr_id = e.get_id("(+ a b)")
    assert expr_id in ids

    nodes = e.eclass_nodes(expr_id)
    # SymbolLang to_string returns the op name
    assert "+" in nodes

def test_checkpoint():
    e = EGraph()
    e.add("a")

    cp = e.checkpoint()
    cp.add("b")

    # Check for presence of 'op: "b"' in dump to be more specific
    assert 'op: "b"' not in e.dump()
    assert 'op: "b"' in cp.dump()

def test_dot():
    e = EGraph()
    e.add("a")
    dot = e.to_dot()
    assert "digraph" in dot

if __name__ == "__main__":
    test_basic_simplification()
    test_cost_functions()
    test_why_equal_checks()
    test_introspection()
    test_checkpoint()
    test_dot()
    print("All manual tests passed!")
