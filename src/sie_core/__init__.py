try:
    from . import sie_core_rust
except ImportError:
    sie_core_rust = None

try:
    from .egraph import EGraph, rewrite
except ImportError:
    from egraph import EGraph, rewrite

__all__ = ["EGraph", "rewrite", "sie_core_rust"]
