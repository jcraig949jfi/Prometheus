# Aether TODO

Currency: 2026-09-23. Written for the instance that boots after a
context reset or a Claude Code upgrade. Read this AFTER the base-role
chain and BEFORE starting anything.

## THE ONE OPEN ITEM

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

## Where the previous round left things (all committed and pushed)

Branch `aether/aeth01-memwall-2026-09-22`, HEAD `75bc0315b` at the time
this was written. Working tree clean, suite green (1020 passed, 5
skipped), `ACTIVE_POD_COUNT 0`.

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
