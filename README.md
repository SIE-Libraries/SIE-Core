# SIE-Core

SIE-Core is an Out-Of-Memory (OOM) prevention library designed to seamlessly supplement [Dask](https://dask.org/) and [CuPy](https://cupy.dev/), making memory management smoother for large-scale Python data processing, distributed computation, and GPU acceleration.

## Features

- **OOM Detection and Prevention:** Monitors memory usage during computations and prevents jobs from exhausting system or GPU memory.
- **Integration with Dask and CuPy:** Works alongside Dask and CuPy, providing an extra safety layer for distributed and accelerated Python workflows.
- **Customizable Policies:** Users can configure memory thresholds and responsive actions tailored to their workloads.
- **Alerts and Logging:** Warns users or triggers callbacks/events when approaching OOM conditions.

## Usage

Full API syntax is under development, but a basic example is shown below:


## Benchmark

_Benchmark results will be presented here. Template below can be filled in as results become available:_

| Library      | Workload Description | Memory Limit | OOM Prevented | Runtime (sec) | Notes         |
|--------------|---------------------|--------------|---------------|---------------|---------------|
| Dask         | [Description]        | [Limit]      | [Yes/No]      | [Time]        | [Comments]    |
| CuPy         | [Description]        | [Limit]      | [Yes/No]      | [Time]        | [Comments]    |

*This table will be updated with real data when available.*

## Contributing

- Fork the repo and submit a pull request.
- All contributions, bug reports, and feature requests are welcome!

## License

Distributed under the MIT License. See `LICENSE` for details.

```
# Additional placeholders for code samples, advanced usage, and troubleshooting.
[Insert scenario/case code here]
```
