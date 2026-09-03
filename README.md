# tool-nvidia

NVIDIA GPU performance monitoring for the [crucible](https://github.com/perftool-incubator/crucible) performance testing framework. Collects GPU metrics using the NVIDIA Management Library (pynvml) during benchmark execution.

## Metrics Collected

- GPU utilization
- GPU temperature
- Memory usage
- Power consumption

## Integration

Nvidia runs as a profiler tool on endpoint nodes with NVIDIA GPUs. It is allowed on profiler, master, worker, and compute collector roles but blocked on client and server roles. The post-processor (`nvidia-post-process.py`) converts raw GPU metrics into crucible's canonical metric format.
