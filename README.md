# SIE-Core

SIE-Core is a Python implementation of an e-graph library, inspired by [egg.rs](https://egraphs-good.github.io/). E-graphs are a powerful data structure for equality saturation, which can be used to build program optimizers, synthesizers, and verifiers.

## Features

- **E-Graph Data Structure:** Efficiently represents many equivalent expressions.
- **Congruence Closure:** Automatically maintains equivalences through rebuilding.
- **Pattern Matching:** Search for sub-graphs using patterns with variables.
- **Equality Saturation:** Apply rewrite rules until a fixed point is reached.

## Usage

```python
from sie_core import EGraph, ENode, Pattern, Rewrite, Runner

# Create an e-graph
eg = EGraph()

# Add expressions: (a * 2) / 2
a = eg.add(ENode("a", ()))
two = eg.add(ENode("2", ()))
mul = eg.add(ENode("*", (a, two)))
div = eg.add(ENode("/", (mul, two)))

# Define rewrite rules
# (x * y) / y -> x
lhs = Pattern(("/", (Pattern(("*", (Pattern("?x"), Pattern("?y")))), Pattern("?y"))))
rhs = Pattern("?x")
rule = Rewrite("div-mul", lhs, rhs)

# Run equality saturation
runner = Runner(eg)
runner.run([rule])

# Check equivalence
assert eg.find(div) == eg.find(a)
```

## Contributing

- Fork the repo and submit a pull request.
- All contributions, bug reports, and feature requests are welcome!

## License

Distributed under the MIT License. See `LICENSE` for details.
