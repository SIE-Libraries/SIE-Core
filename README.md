# SIE-Core

SIE-Core is a high-performance Python e-graph library powered by Rust and [egg.rs](https://egraphs-good.github.io/).

## Features

- **Rust Backend:** Leverages the power of `egg.rs` for efficient e-graph operations.
- **Pythonic API:** Simple and intuitive interface for Python users.
- **Equality Saturation:** Automatically find the best version of an expression based on rewrite rules.
- **Extraction:** Retrieve the optimized expression with minimal cost.

## Installation

```bash
pip install .
```

## Usage

```python
from sie_core import EGraph, rewrite

e = EGraph()

# Add expressions (prefix notation)
e.add("(+ a 0)")
e.add("(+ 0 a)")

# Define rewrite rules
rules = [
    rewrite("(+ ?x 0)", "?x"),
    rewrite("(+ 0 ?x)", "?x"),
]

# Run equality saturation
e.run(rules)

# Extract the best expression
print(e.best("(+ a 0)"))  # Output: a
```

## API Reference

### `EGraph`
- `add(expr: str)`: Add an expression in prefix notation.
- `run(rules: list, iterations: int = None)`: Run equality saturation.
- `best(expr: str) -> str`: Get the best equivalent expression.
- `stats() -> dict`: Get execution statistics.
- `dump() -> str`: Get a debug dump of the e-graph.

### `rewrite(lhs: str, rhs: str, name: str = None)`
- Creates a rewrite rule from a left-hand side pattern to a right-hand side pattern.

## License

Distributed under the MIT License. See `LICENSE` for details.
