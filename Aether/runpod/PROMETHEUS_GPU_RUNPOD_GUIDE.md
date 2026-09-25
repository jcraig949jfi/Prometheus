# Running a GPU experiment on RunPod

For any Prometheus seat. You do not need to read Aether's code, learn
the RunPod API, build a Docker image, or handle a credential.

Currency: 2026-09-24. Every command below is executable today; anything
not yet qualified says so explicitly rather than being described as if
it worked.

## 1. What the platform does

You provide a directory with your code and a small JSON spec. The
platform gives you:

- deterministic packaging with an immutable bundle hash
- a zero-dollar dry run that shows exactly what would happen
- a cost projection that separates overhead from compute
- pod launch on a STOCK image, with your dependencies installed at boot
- credential scrubbing before your code runs
- telemetry, artifact retrieval, cleanup, and a machine-readable receipt

What it does NOT do: build or publish containers. Your module is fetched
at boot as a checksummed bundle and unpacked onto a stock RunPod image.

## 2. The 60-second version

```bash
cd Aether/runpod
cp -r examples/hello_gpu /tmp/my_module
# edit /tmp/my_module/run.py and module_spec.json

python -m prometheus_gpu.cli estimate /tmp/my_module/module_spec.json
python -m prometheus_gpu.cli dry-run  /tmp/my_module/module_spec.json
python -m prometheus_gpu.cli rehearse /tmp/my_module/module_spec.json
```

`examples/param_sweep/` is the fuller one to copy if your experiment is a
sweep or a scan: it counts its own work units, records its seed so the run
can be re-derived, and emits its effective configuration in telemetry.

The dry run prints the bundle hash, the exact sanitized pod request, the
cost breakdown, the current pod inventory, and a findings list. It
cannot create a pod.

## 3. The minimal module spec

Two fields are mandatory. Everything else has a defensible default.

```json
{"name": "my-module", "entrypoint": "run.py"}
```

A realistic one:

```json
{
  "name": "my-module",
  "version": "1",
  "entrypoint": "run.py",
  "args": ["--steps", "1000"],
  "dependencies": {"pip": ["numpy==2.2.0", "cupy-cuda12x==13.3.0"]},
  "gpu": {"class": "NVIDIA RTX A4000", "count": 1, "cloud": "SECURE"},
  "disk_gb": 10,
  "max_runtime_s": 600,
  "artifacts": ["out/result.json", "out/telemetry.jsonl"],
  "canary": "python3 -c \"import cupy; cupy.arange(8).sum()\"",
  "env_allowlist": ["MY_SEED"],
  "env": {"MY_SEED": "7"},
  "work_units": {"name": "steps", "estimate": 1000.0}
}
```

Full field reference: `MODULE_CONTRACT.md`.

Things the validator REFUSES, because each one costs money or loses
data:

| refused | why |
|:--|:--|
| no `max_runtime_s` bound, or over 24 h | an unbounded run is an unbounded bill |
| unpinned pip requirement | the bytes that ran cannot be reconstructed |
| absolute or `..` paths in `entrypoint`/`artifacts` | escapes the module directory on the pod |
| backslashes in paths | a legal filename character on Linux, so it becomes one strange file |
| a provider credential in `env_allowlist` | credentials belong to the controller |
| `work_units.estimate` of 0 | it is a denominator |

## 4. How your dependencies get installed

From `dependencies.pip`, at boot, with `pip install --no-cache-dir`,
AFTER the bundle checksum is verified and BEFORE your code runs. Pin
everything: the platform refuses unpinned requirements so that a run is
reproducible.

If you need something pip cannot install, say so and the platform grows
a path for it. Do not build a custom image just to add a package.

## 5. Requesting a GPU

`gpu.class` is a RunPod SKU string, e.g. `NVIDIA A40`,
`NVIDIA RTX A4000`, `NVIDIA RTX A5000`, `NVIDIA L4`.

**Pick the cheapest GPU that fits your memory need, not the fastest.**
A short job is dominated by fixed overhead, so a slower cheaper card
often finishes for less money even though it takes longer. `estimate`
will show you. See `COST_MODEL.md`.

## 6. Dry run, and what its findings mean

```bash
python -m prometheus_gpu.cli dry-run module_spec.json --workload-seconds 300
```

It validates the spec, builds the bundle and hashes it, records git
identity, constructs the exact request, reads the live pod inventory,
projects cost, and emits the receipt skeleton. Findings are advice, not
errors:

- *no artifacts declared* -- the run would leave no results
- *no canary declared* -- a broken environment is not caught until your
  workload fails
- *N pod(s) already active* -- a launch would add to them
- *module directory is git-dirty* -- the bundle is reproducible only
  from its own hash, not from a commit
- *overhead is N% of this run* -- consider a longer workload or a
  cheaper GPU

Pass `--out plan.json` to keep the plan. The plan IS the receipt
skeleton, so what you validated is what runs.

## 7. Cost estimate

```bash
python -m prometheus_gpu.cli estimate module_spec.json --workload-seconds 300
```

Reports hourly rate, the overhead breakdown, compute time, total,
overhead fraction, and cost per unit of YOUR work unit. When you give no
`--workload-seconds` it uses `max_runtime_s` and labels the result a
CEILING.

## 8. Rehearse, then launch

### Rehearse -- $0.00

```bash
python -m prometheus_gpu.cli rehearse module_spec.json [--verbose]
```

A dry run proves the *request* is well formed. A rehearsal flies the
**whole controller path** against a fake provider -- create, wait for
ready, poll telemetry, retrieve artifacts, terminate, confirm absence,
write a receipt -- using YOUR spec, and prints the receipt you would get.
It resolves no credential and holds nothing that can reach RunPod. Run it
before you spend anything.

### Launch

**Not yet available as `prometheus-gpu run`.** The controller in
`prometheus_gpu/launch.py` is complete and qualified against the fake
provider, including the cases that cost money: a lost create response, an
unreadable inventory, a pod hidden from the listing, a terminate that
will not acknowledge, a budget ceiling, and a controller that raises
mid-run. What it has **not** done is fly on hardware, and until it has,
exposing `run` would invite spending through an unproven path.

Until it lands, a real run goes through the qualified orchestrators in
`aeth01_firstlight/` or `aeth02_circuitry/`, or through Aether.

What exists today: `estimate`, `dry-run`, `rehearse`, `bundle`,
`inventory`, `cleanup`, `validate-telemetry`, `validate-receipt`. This
section is updated when `run` is qualified.

## 9. Telemetry

Append JSON lines to `$PROMETHEUS_TELEMETRY_PATH`. Every record should
carry both a UTC timestamp and a monotonic elapsed time; the platform
adds them if you omit them.

```python
import json, os, time
path = os.environ["PROMETHEUS_TELEMETRY_PATH"]
with open(path, "a") as fh:
    fh.write(json.dumps({"kind": "progress", "step": 10,
                         "my_metric": 0.42}) + "\n")
    fh.flush()
```

Use any keys you like for your own metrics. The platform never forces
your workload into Aether's vocabulary. Schema: `TELEMETRY_SCHEMA.md`.

## 10. Artifacts

List them in `artifacts`, relative to `$PROMETHEUS_ARTIFACT_DIR`. Keep
them small enough to travel: the artifact channel serves at most 8 MB
and keeps the FIRST 8 MB, so an overrun silently discards the END of
your run. Compress or subsample rather than hoping.

## 11. Cleanup

```bash
python -m prometheus_gpu.cli inventory
python -m prometheus_gpu.cli cleanup --all
```

Cleanup reports four DIFFERENT claims, and they are not
interchangeable:

| claim | meaning |
|:--|:--|
| `terminate_acknowledged` | the provider accepted a terminate |
| `observed_absent` | the pod is no longer in the inventory |
| `operational_cleanup` | nothing we know of is still running |
| `billing_reconciled` | **provider billing data was obtained** |

The last is always `false` unless the provider was actually asked. A run
may never claim reconciliation from wall-clock arithmetic.

## 12. Failure and recovery

Read `FAILURE_PLAYBOOK.md`. The one rule worth memorising:

> A failed create does not tell you whether a pod exists. Never retry a
> create blindly. Read the inventory first; adopt what is there; and if
> the inventory read ALSO fails, stop rather than guess.

## 13. Your own metrics

Anything you write to the telemetry file. For cost per unit of useful
work, declare `work_units` and the platform reports dollars per unit in
your own denominator: site-ticks, candidates, evaluations,
simulation-steps, whatever your science counts.

## 14. Reproducing a historical run

A receipt carries the bundle sha256, the git commit, the spec hash, the
pinned dependency list, the image, and the GPU. Rebuild the bundle from
the same commit and compare the hash: identical hash means identical
bytes ran. Bundling is deterministic, so this works from any machine at
any time.

If the receipt says the module was git-dirty, the commit is not
sufficient and the bundle hash is the only identity.

## 15. If the platform gets in your way

That is a platform defect, not your problem to work around. Report it to
Aether with the spec that failed. The success criterion for this system
is that a fresh seat can package and launch a GPU experiment without
reading Aether's implementation; if you had to, we have work to do.
