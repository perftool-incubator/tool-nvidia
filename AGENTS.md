# Tool-nvidia

## Purpose
Crucible tool for collecting NVIDIA GPU performance metrics (utilization, temperature, memory, power) during benchmark execution using the NVIDIA Management Library (`pynvml`).

## Languages
- Bash: start/stop wrapper scripts (`nvidia-start`, `nvidia-stop`)
- Python: GPU sampling and post-processing (`nvidia-collect`, `nvidia-post-process`)

## Key Files
| File | Purpose |
|------|---------|
| `nvidia-start` | Launches `nvidia-collect` in the background with configured interval |
| `nvidia-stop` | Sends SIGINT to `nvidia-collect` and compresses output files with xz |
| `nvidia-collect` | Initializes `pynvml`, queries GPU metrics at intervals, and writes aligned CSV output |
| `nvidia-post-process` | Parses collected data into crucible CDM metrics (`pwr`, `util`, `mem`, `temp`) |
| `rickshaw.json` | Rickshaw integration: collector scripts, blacklist/whitelist |
| `workshop.json` | Engine image build: requires `pynvml` |
| `tool-metadata.json` | Machine-readable description and CDM-indexed status (consumed by `crucible tools list`) |
| `multiplex.json` | Parameter validation rules and `defaults` preset for multiplex (mirrors benchmark `multiplex.json`) |

## Configuration
- `--interval <seconds>` — GPU polling interval in seconds (default: `10`)

## Architecture
- `nvidia-start` — Launches `nvidia-collect --interval $interval >nvidia-output.txt &` in background and records PID to `nvidia-pids.txt`
- `nvidia-collect` — Calls `pynvml.nvmlInit()`, queries all NVIDIA GPUs on the system for utilization rates, temperature, memory stats, and power usage, and prints formatted records
- `nvidia-stop` — Sends SIGINT to `nvidia-collect`, waits for termination, and compresses `nvidia-output.txt` with xz
- `nvidia-post-process` — Reads `nvidia-output.txt.xz`, parses CSV records, and logs CDM metrics (`source`: `nvidia`, `types`: `pwr`, `util`, `mem`, `temp`)

## Testing
- Run post-processor locally: `cd <tool-data-dir> && TOOLBOX_HOME=/opt/crucible/subprojects/core/toolbox python3 /opt/crucible/subprojects/tools/nvidia/nvidia-post-process`
- Validate syntax: `python3 -c "import py_compile; py_compile.compile('nvidia-post-process', doraise=True); py_compile.compile('nvidia-collect', doraise=True)"`
- Full integration: `crucible run <run-file.json>` with nvidia tool configured on GPU-equipped node

## Conventions
- Primary branch is `main`
- Runs as a profiler tool on master/worker/profiler/compute roles, blocked on client/server
- Requires NVIDIA GPUs and drivers on the target host
- Standard Bash modelines and 4-space indentation
- Python code follows 4-space indentation with standard modelines
