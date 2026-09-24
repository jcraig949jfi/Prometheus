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

## Commands

```bash
python -m prometheus_gpu.cli estimate  spec.json [--workload-seconds N]
python -m prometheus_gpu.cli dry-run   spec.json [--out plan.json]
python -m prometheus_gpu.cli bundle    spec.json [--out bundle.tar.gz]
python -m prometheus_gpu.cli inventory
python -m prometheus_gpu.cli cleanup   [--pod ID ...] [--all]
python -m prometheus_gpu.cli validate-telemetry telemetry.jsonl
python -m prometheus_gpu.cli validate-receipt   receipt.json
```

`estimate` and `dry-run` cost nothing and cannot create a pod. `run` is
deliberately absent until the launch path has flown — see the guide, s8.

## Layout

| path | what it is |
|:--|:--|
| `prometheus_gpu/` | the platform: spec, bundle, secrets, provider, cost, telemetry, receipt, dry run, CLI |
| `examples/hello_gpu/` | the minimal module, meant to be copied |
| `aeth01_canary/` | the qualified RunPod client and GPU canary |
| `aeth01_firstlight/`, `aeth02_circuitry/` | Aether's own campaign orchestrators |

`pod_service.py` is not modified by anything here.

## Gate

```bash
python -m pytest Aether/test/test_prometheus_gpu.py -q
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
