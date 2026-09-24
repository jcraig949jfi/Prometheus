# Aether TODO

Currency: 2026-09-24. Written for the instance that boots after a
context reset or a Claude Code upgrade. Read this AFTER the base-role
chain and BEFORE starting anything.

## TWO OPEN ITEMS

**1. AETHER RUNPOD ENGINEERING LADDER (2026-09-24) -- PRIORITY.**
Turn everything learned from RunPod into a reusable Prometheus GPU
experimentation system. Verbatim, with a manifest:

    roles/Aether/prompts/2026-09-24_runpod_engineering_ladder/DIRECTIVE.md

Budget: $5 incremental, SEPARATE from AETH-02's. Rungs: zero-dollar dry
run -> tiny pod -> scale up -> long run + failure injection -> 2-3 pod
fan-out -> a FOREIGN SEAT'S module through the same machinery. The
strongest success test is whether a fresh seat can package and launch a
GPU experiment without reading Aether's implementation.

**2. AETH-02 NATIVE CIRCUITRY** -- the science, which continues as the
engineering campaign's reference workload.

## LADDER PROGRESS (2026-09-24)

**Iteration 0 DONE, $0.00.** `Aether/runpod/prometheus_gpu/`, the
`examples/hello_gpu/` module, and the six documents named by the
directive. 59 tests in `Aether/test/test_prometheus_gpu.py`.

Entry point for a fresh seat: `Aether/runpod/README.md`. Do not start by
reading the platform source; the guide is meant to be sufficient and if
it is not, that is the defect to fix.

Two bugs the tests found before any pod: `os.path.isabs("/abs/path")` is
False on a Windows controller, so host path rules were deciding what is
legal on a Linux pod; and the package was originally named `platform`,
shadowing the stdlib module.

**The launch path EXISTS and is qualified against the fake provider**
(`prometheus_gpu/launch.py`, 20 tests in
`Aether/test/test_prometheus_gpu_launch.py`). It has not flown on
hardware, which is the only thing missing. `python -m prometheus_gpu.cli
run` is therefore still absent; `rehearse` is the zero-dollar substitute
and flies the whole controller path against the fake using a seat's own
spec.

Qualified against the fake, all cases that cost money: a lost create
response, an unreadable inventory, a pod hidden from the listing, a
terminate that will not acknowledge, the budget ceiling, `max_runtime_s`,
and a controller that raises mid-run. The fake's `leaked()` is asserted
empty in every one.

Next rung (Iteration 1): point `launch.Controller` at `RunPodProvider`
for one tiny pod, ~$0.05, and expose `run` if it holds. Requires the
AETH-02 pod to be down first -- one pod at a time is a precondition the
controller now enforces itself.

A bug worth remembering, found by the launch tests: the teardown
`finally` originally forced `result = NOT_RUN` whenever no pod id was
held. An UNRESOLVED create also holds no id, so a pod that might have
been billing would have been recorded as a clean non-event. Only a
provider-confirmed clean failure may be downgraded to NOT_RUN.

**Cost calibration correction.** The preregistered $0.83 per 2048^2
x 50,000-tick trajectory was 7.2% low; measured $0.889. Cause: a
throughput figure from an uninstrumented 4096^2 run was carried to an
instrumented 2048^2 run without re-measuring. Measured rates now live in
`Aether/runpod/COST_MODEL.md`; take them from there rather than
re-deriving.

## THE AETH-02 ITEM

**AETH-02 NATIVE CIRCUITRY ROUND -- NOT STARTED.**

Authoritative text, verbatim, with a manifest:

    roles/Aether/prompts/2026-09-23_native_circuitry/DIRECTIVE.md
    roles/Aether/prompts/2026-09-23_native_circuitry/00_PROVENANCE.md

Verify before acting on it:

    python -m comms.manifest verify roles/Aether/prompts/2026-09-23_native_circuitry

Nothing in that round has been done. Do not infer progress from the
existence of the First Light tooling.

Note: a comms self-post was tried as an extra pointer and does NOT
deliver (a seat's own message never reaches its own queue; message
537 records the attempt). The committed files are the working
routes.

## BOOT: integration DONE, boot from main

**`origin/main` carries the authoritative Aether lane as of
`183388e39` (2026-09-23).** Boot normally from `origin/main`; no branch
override is needed and none is in `roles/Aether/WAKE.md` any more.

The merge: `origin/main` (`5bb013a7f`, 2598 ahead of the branch) merged
into `aether/aeth01-memwall-2026-09-22` (47 ahead) with **0 conflicts**,
then fast-forwarded to main. The Aether suite on the MERGED tree was
1020 passed, 5 skipped, 0 failed -- identical to pre-merge. Outside
`Aether/` and `roles/Aether/`, the push changed exactly two
`.gitignore` lines. The kernel hash was unchanged by the merge
(`138b32dccd1d69ed`) and the directive's bytes on main match its
manifest.

`roles/Aether/WAKE.md` keeps the paste block, now with the plain task
line "Read roles/Aether/TODO.md first.".

## Where the previous round left things (all committed and pushed)

On `origin/main` as of `183388e39`. Working tree clean, suite green
(1020 passed, 5 skipped), `ACTIVE_POD_COUNT 0`. The next round should
cut a fresh task branch from `origin/main` in the normal way rather
than continuing `aether/aeth01-memwall-2026-09-22`, which has served
its purpose.

Done on 2026-09-22, in order:

- memory-wall round: peak allocation 240.00 -> 113.01 bytes/site, and
  16384^2 = 268 M sites now runs on one A40 (`MEMORY_WALL_MOVED`).
  `Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md`
- Phase A: the uint64 scalar-overflow warning removed at its source via
  `mix64_scalar`. `Aether/AETH-01/MIX64_SCALAR_REPAIR_2026-09-22.md`
- tier-1 observatory built from nothing: `Aether/observatory/`,
  18 known-answer tests including a read-only guard
- 36-config CPU scout, $0: `Aether/AETH-01/SCOUT_FINDINGS_2026-09-22.md`
- First Light, 6 worlds x 4096^2 x 5,000 ticks, $2.022:
  `Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md`

## What the new round must build, because it does not exist

1. **A causal-graph observatory (Track 2).** The current observatory
   emits lattice-wide scalars, per-field change rates and 64-block
   coarse maps. It emits **no edges**. Track 2 is a build, not a
   configuration change, and it is the largest piece of work in the
   directive. The kernel does not currently surface which source won
   which contest, so getting `source -> target` edges at all needs a
   way to recover arbitration outcomes without changing `aeth01.v1`.
2. **Full-resolution window retention (Track 5).** Nothing today keeps
   anything below the 64-site block scale. The selection rule must be
   preregistered, in its own commit, before the run.
3. **A long-horizon CPU/GPU digest comparison** (the determinism
   check). Only tick-1 agreement at 4096^2 and 7-tick agreement at
   16..2048 are established today.
4. **GPU memory sampling.** The First Light runner never recorded
   `mem_used_mb`; that gap is why the directive asks for it explicitly.

## Known constraints carried into the round

- Do not redesign `aeth01.v1`. Do not add steering or reward.
- Both kernel copies must stay AST-identical
  (`test_aeth01_canary_parity.py`), and the frozen A40 digests in
  `test_aeth01_memory_footprint.py` must keep reproducing.
- The terminology contract is enforced by
  `test_aeth01_terminology_audit.py` over the whole `Aether/` tree; it
  caught 13 violations in the last round. Write "perturbation", not the
  deprecated biology term, and check before pushing.
- Run the full suite BEFORE pushing, not after. Commit `cf7e4efea` went
  out with a red test because that order was wrong.
- Budget is the directive's own up-to-$3; roughly $2.09 of the previous
  authorization was already spent. Confirm rather than assume carry-over.
- One pod at a time; verify `ACTIVE_POD_COUNT 0` before and after.
  `Aether/runpod/aeth01_firstlight/` has the working orchestrator with
  a controller-side dollar ceiling and a pod-side wall clock; bring the
  artifact server up BEFORE the science or a mid-run termination
  destroys the evidence.

## Standing seat defects, unchanged and not blocking

- `roles/Aether/RESPONSIBILITIES.md` still describes a pre-charter seat
  with no lane and no science. Stale since 2026-09-20; needs a rewrite
  around `Aether/AETHER_DOCTRINE.md`, with the old body moved to
  `roles/Aether/superseded/`.
- `BACKLOG_H0H5.md` is still the 3-item provisional file, below the
  schema's 20-item floor.
- `roles/base-role/INHERITANCE.md` rows 11 and 77 still say the charter
  is pending.
- The fleet-wide base-role self-test is red on a Nyx prompt manifest
  (`dc41abff1393 != dbd639ef6ee7`), reported by this seat on
  2026-09-19 and unfixed. Not caused here; do not chase it.
