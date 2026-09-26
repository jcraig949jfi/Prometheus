# Aether/runpod

GPU experiments on RunPod, for any Prometheus seat.

## Start here

| if you want to | read |
|:--|:--|
| run a GPU experiment | [PROMETHEUS_GPU_RUNPOD_GUIDE.md](PROMETHEUS_GPU_RUNPOD_GUIDE.md) |
| know what to declare | [MODULE_CONTRACT.md](MODULE_CONTRACT.md) |
| report progress from inside a run | [TELEMETRY_SCHEMA.md](TELEMETRY_SCHEMA.md) |
| know what a run may claim afterwards | [RUN_RECEIPT_SCHEMA.md](RUN_RECEIPT_SCHEMA.md) |
| know what it will cost | [COST_MODEL.md](COST_MODEL.md) |
| recover from something going wrong | [FAILURE_PLAYBOOK.md](FAILURE_PLAYBOOK.md) |

Copy `examples/hello_gpu/` and edit it. It is two files.

Two examples ship, and the second one is the honest check:

| example | what it is |
|:--|:--|
| `examples/hello_gpu/` | the smallest useful module; copy this |
| `examples/param_sweep/` | an ordinary experiment written from ANOTHER seat's point of view: counts `evaluations`, unrelated to Aether's physics, imports nothing from the platform |
| `examples/gpu_load/` | sustained GPU load for measuring the platform: matmul throughput, per-step latency, a memory ballast and a multi-MB artifact; reads `PROMETHEUS_WORK_UNITS` so it can be scouted |

Both are EXECUTED by `Aether/test/test_prometheus_gpu_examples.py`, which
validates their telemetry and checks every declared artifact was actually
written. `hello_gpu` shipped emitting `utc`/`monotonic_s`, which the
telemetry validator rejects, and nothing caught it until the example was
run through the validator rather than trusted.

## Commands

```bash
python -m prometheus_gpu.cli estimate  spec.json [--workload-seconds N]
python -m prometheus_gpu.cli dry-run   spec.json [--out plan.json]
python -m prometheus_gpu.cli bundle    spec.json [--out bundle.tar.gz]
python -m prometheus_gpu.cli rehearse  spec.json [--verbose]
python -m prometheus_gpu.cli inventory
python -m prometheus_gpu.cli cleanup   [--pod ID ...] [--all]
python -m prometheus_gpu.cli validate-telemetry telemetry.jsonl
python -m prometheus_gpu.cli validate-receipt   receipt.json
```

`estimate`, `dry-run` and `rehearse` cost nothing and cannot create a
pod. `rehearse` flies the entire controller path against a fake provider
using your spec.

A real launch goes through `flight.py`, generic over any module directory
(build, dry run, rehearse, `--go`, `--scout`, `--pin-gpu`, `--calibrate`)
— see the guide, s8. It has flown on hardware in Iterations 1 and 2.

## Layout

| path | what it is |
|:--|:--|
| `prometheus_gpu/` | the platform: spec, bundle, secrets, provider, cost, telemetry, receipt, dry run, launch, CLI |
| `examples/hello_gpu/` | the minimal module, meant to be copied |
| `aeth01_canary/` | the qualified RunPod client and GPU canary |
| `aeth01_firstlight/`, `aeth02_circuitry/` | Aether's own campaign orchestrators |

`pod_service.py` is not modified by anything here.

## Gate

```bash
python -m pytest Aether/test/test_prometheus_gpu.py -q
python -m pytest Aether/test/test_prometheus_gpu_launch.py -q
python -m pytest Aether/test/test_prometheus_gpu_examples.py -q
python -m pytest Aether/test/test_prometheus_gpu_scout.py -q
python -m pytest Aether/test/test_prometheus_gpu_iteration2.py -q
```

Run it as its own command and read the result. Piping a gate into `tail`
inside an `&&` chain takes the exit status from `tail`, which is how two
red suites were once pushed as green — playbook entry 6.

## Rules that are not negotiable

- Credentials belong to the controller. A module never receives one, and
  a spec that asks for one is refused.
- A failed create does not tell you whether a pod exists. Read the
  inventory, adopt what is there, and if the inventory read also fails,
  stop.
- No run reports clean because a listing omitted a pod.
- No run claims billing reconciliation without provider billing data.
