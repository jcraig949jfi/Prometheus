# Sweep Override Protocol

**Purpose:** define how and when a `BLOCK` verdict from a pattern auto-sweep
can be overridden, so that the block is a gate, not a wall.

**Scope:** applies to `harmonia.sweeps.sweep_signature()` outcomes used by
`agora.register_specimen.register()` and `agora.tensor.push.push_tensor()`.
**Authority:** Harmonia conductor session (canonical name
`Harmonia_M2_sessionA`) or James directly.

---

## Default posture

Every new SIGNATURE that reaches the ingestion path is swept. If the runner
returns `overall = BLOCK`, the ingestion call raises `SweepBlocked` by
default. The blocked SIGNATURE does not land in `signals.specimens`. The
tensor push does not halt on a BLOCK (batch op) but logs the block to
`agora:harmonia_sync` under `type=PATTERN_30_BLOCK`.

## When override is legitimate

Four situations where `sweep_override=True` is the right call:

1. **Known Level-4 calibration cell.** Calibration anchors (F001–F005, F008,
   F009) are Pattern 30 Level 4 by design — the "correlation" is a theorem
   verification. Override with reason `calibration_anchor:<F-ID>`.

2. **Retrospective re-run of an already-retracted cell.** If a BLOCK fires
   on a cell we already know was retracted (F043's -2 cells), the sweep is
   doing its job but the retraction predates this filter. Override with
   reason `already_retracted:<F-ID>:<retraction_commit>`.

3. **Pattern 30 lineage registry error.** If the lineage check is *wrong*
   — e.g., the registered algebraic_lineage overclaims coupling — correct
   the registry first, then re-run without override. Do not override as a
   shortcut around a bad registry entry; fix the registry.

4. **Conductor-reviewed intentional algebraic observation.** A Level 2/3
   finding reported *as* an algebraic observation (not as arithmetic
   evidence) is epistemically legitimate. Override with reason
   `algebraic_observation_only:<F-ID>`, and verify the claim wording in the
   tensor description uses algebraic-observation language.

## When override is NOT legitimate

Never override to "unblock" a measurement that you would not also be
comfortable retracting later if the filter turned out correct. If you are
tempted to override to save work, don't — debug the finding instead.

- **Not a valid reason:** "the effect is too big to be just algebra"
  (F043 had z=-348 and was pure algebra).
- **Not a valid reason:** "we already published" (nothing is published
  from this substrate; retractions are free).
- **Not a valid reason:** "the sweep is slow" (run it anyway; slow is
  cheaper than wrong).

## Override logging

Every override writes a record to
`harmonia/memory/sweep_results_log.md` (via `runner.log_outcome`). The
record carries:

- `context_id` (task_id + feature_id)
- full sweep verdicts
- `override: true`
- `override_reason: <string>`
- `at: <ISO timestamp>`

The log is append-only and grep-friendly. A conductor-initiated quarterly
audit (per `gen_06_pattern_autosweeps.md` epistemic discipline bullet 1)
samples ~20 BLOCKED or OVERRIDDEN cells and checks whether the decision
was correct. Mis-overrides are recorded in `abandon_log.md`.

## Code pattern

```python
from harmonia.sweeps import sweep_signature
from harmonia.sweeps.pattern_30 import CouplingCheck

outcome = sweep_signature(
    coupling_check=CouplingCheck(...),
    pattern20_check=...,
    pattern19_new=...,
    pattern19_prior=...,
)

# Default path: raises SweepBlocked if outcome.overall == 'BLOCK'
register(
    task_id=...,
    feature_id='F003',
    status='calibration_confirmed',
    # ... other args ...
    sweep_outcome=outcome,
)

# Override path (justified):
register(
    ...,
    sweep_outcome=outcome,
    sweep_override=True,
    sweep_override_reason='calibration_anchor:F003',
)
```

Never call `register()` with `sweep_override=True` and an empty reason —
the call fails fast with `ValueError`.

## Versioning

The sweep code modules (`pattern_30.py`, `pattern_20.py`, `pattern_19.py`,
`runner.py`) will eventually be promoted as `computation` symbols once
that symbol type ships (per `long_term_architecture.md §2.1`). Until
then, the modules are versioned by git commit, and any rule change
(severity thresholds, ratio cutoffs) bumps an inline `__module_version__`
constant. A sweep result recorded in `sweep_results_log.md` references
the commit and module-version under which it was computed.

---

*v1.0 — 2026-04-20 — sessionA, accompanying gen_06 initial implementation.*
