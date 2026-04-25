from typing import List, Optional, Dict, Any, Union, Iterator
import sys
import importlib

# Robust import of the Rust extension
sie_core_rust = None

# 1. Try importing from the installed package
try:
    import sie_core.sie_core_rust as m
    sie_core_rust = m
except ImportError:
    # 2. Try importing relatively (if we are inside the package)
    try:
        from . import sie_core_rust as m
        sie_core_rust = m
    except (ImportError, ValueError):
        # 3. Try importing directly (if it's in PYTHONPATH)
        try:
            import sie_core_rust as m
            sie_core_rust = m
        except ImportError:
            sie_core_rust = None

class EGraph:
    def __init__(self):
        if sie_core_rust is None:
            raise ImportError(
                "sie_core_rust extension not found. "
                "Ensure the package is installed correctly (e.g., via `pip install .`)."
            )
        self._egraph = sie_core_rust.RustEGraph()

    def add(self, expr: str) -> None:
        self._egraph.add(expr)

    def run(self, rules: List['RewriteRule'], iterations: Optional[int] = None) -> List[Any]:
        raw_rules = [(r.name, r.lhs, r.rhs) for r in rules]
        return self._egraph.run(raw_rules, iterations)

    def run_iter(self, rules: List['RewriteRule'], iterations: int = 10) -> Iterator[Any]:
        """Runs rewrite rules iteration by iteration."""
        for _ in range(iterations):
            prev_nodes = self.stats()["nodes"]
            prev_classes = self.stats()["classes"]

            step_info = self.run(rules, iterations=1)
            if not step_info:
                break

            yield step_info[0]

            # Simple saturation check
            curr_stats = self.stats()
            if curr_stats["nodes"] == prev_nodes and curr_stats["classes"] == prev_classes:
                break

    def extract(self, expr: str, cost: str = "size") -> str:
        """Return best equivalent expression according to cost function."""
        return self._egraph.extract(expr, cost)

    def best(self, expr: str) -> str:
        """Alias for extract with default cost."""
        return self.extract(expr, cost="size")

    def are_equal(self, expr1: str, expr2: str) -> bool:
        return self._egraph.are_equal(expr1, expr2)

    def explain(self, expr: str) -> str:
        return self._egraph.explain(expr)

    def why_equal(self, a: str, b: str) -> str:
        return self._egraph.why_equal(a, b)

    def stats(self) -> Dict[str, Any]:
        return self._egraph.stats()

    def dump(self) -> str:
        return self._egraph.dump()

class RewriteRule:
    def __init__(self, name: str, lhs: str, rhs: str):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs

def rewrite(lhs: str, rhs: str, name: Optional[str] = None) -> RewriteRule:
    """Functional style for creating rewrite rules."""
    if name is None:
        name = f"{lhs} -> {rhs}"
    return RewriteRule(name, lhs, rhs)
