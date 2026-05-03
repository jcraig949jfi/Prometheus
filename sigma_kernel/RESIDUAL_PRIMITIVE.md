# Residual primitive — sigma_kernel.residuals

Residual-aware falsification, sidecar extension to the v0.1 kernel.
Implements the proposal at
`stoa/discussions/2026-05-02-techne-on-residual-aware-falsification.md`.

## What's shipped

- `sigma_kernel/residuals.py` — `ResidualExtension` sidecar:
  - `Residual` dataclass (typed record of a non-uniform falsification)
  - `SpectralVerdict` dataclass (replaces bivalent `VerdictResult`
    when callers want spectral output)
  - `RefinedClaim` dataclass (a claim born from `REFINE`, carrying
    `refinement_depth` + `cost_budget_remaining`)
  - `record_residual(...) -> Residual` (auto-classifies + persists)
  - `_classify_residual(...)` (the four-rule classifier; see below)
  - `REFINE(claim, residual, cap) -> RefinedClaim` (the new opcode;
    requires `signal`-class residual + capability)
  - `record_meta_claim(target_battery_id, evidence_residuals,
    hypothesis, cap) -> Claim` (auto-spawn path for drift residuals)
  - `list_residuals(...)` and `refinement_chain(claim_id)` for
    inspection
- `sigma_kernel/migrations/003_create_residual_tables.sql` — Postgres
  migration. Mirror SQLite schema baked into `residuals.py`.
- `sigma_kernel/residual_benchmark.py` — the 30-residual benchmark
  (10 signal + 10 noise + 10 drift) with `run_benchmark(...)` runner.
- `sigma_kernel/test_residuals.py` — math-tdd test coverage:
  - 5 authority tests (Mercury, Gaussian, OPERA, Lehmer half-budget,
    depth-7 BudgetExceeded)
  - 4 property tests (determinism, geometric decay,
    classification-in-set, RefinementBlocked)
  - 6 edge tests (empty subset, magnitude OOB, missing cap, consumed
    cap, depth-20 budget, no-calibration)
  - 5 composition tests (full pipeline, **30-residual benchmark
    load-bearing acceptance**, chain-walks-to-root, cost conservation,
    META_CLAIM auto-spawn)

## What's deferred (explicitly)

- **Spectral oracle integration.** The proposal §4.3 outlines
  extending `FALSIFY` to emit `SpectralVerdict` directly from the Ω
  oracle subprocess. The MVP ships the type but `record_residual` is
  invoked from caller code (e.g., a battery harness) rather than
  auto-fired by `kernel.FALSIFY`. Wiring in is a 1-day extension when
  battery harnesses opt in.
- **Per-residual variance computation from raw subset.** The
  classifier currently reads `coeff_variance` from the `failure_shape`
  dict. Production should compute variance directly from
  `surviving_subset['items']` when present. Not on the critical path
  for the day-1 acceptance test.
- **Calibration-anchor live read.** The MVP requires the caller to
  pass `calibration_signatures` at construction. Production should
  pull the kernel's current calibration anchor fingerprints
  (e.g., from a `calibration_anchors` table). The current path lets
  agents experiment with their own fingerprint maps without coupling
  to a global calibration store.

## Benchmark accuracy result (load-bearing)

The 30-residual benchmark, run on commit-time:

```
accuracy:                          1.000  (30 / 30)
false_positive_signal_count:       0      (zero, on the 10 noise items)
per_class.signal.precision:        1.000
per_class.signal.recall:           1.000
per_class.noise.precision:         1.000
per_class.noise.recall:            1.000
per_class.instrument_drift.prec:   1.000
per_class.instrument_drift.rec:    1.000
```

The day-4 acceptance criterion (>=80% accuracy AND zero FP `signal` on
known-noise) is met with margin. The primitive ships.

Cautionary note: the benchmark is hand-curated, and its noise residuals
are explicitly tagged with `coeff_variance` < 0.05 while signal
residuals carry > 0.85. This means the variance heuristic operates in a
generous regime. The first hostile real-world residual that lands in
the gap (variance ~ 0.5) will tell us whether the heuristic is robust
or whether the four-subclass canonicalizer needs to take over more of
the signal-detection work. The benchmark is necessary, not sufficient.

## Three composing stopping rules — implemented

Per the proposal §3, three rules ship from day zero:

1. **Cost-budget compounding (§3.1).** Each `REFINE` halves the
   parent's `cost_budget_remaining`. When budget falls below
   `MIN_USEFUL_BUDGET_SECONDS` (0.1 s default), `BudgetExceeded` is
   raised. With the default 10 s root budget, the chain exhausts at
   depth 7 (10 * 0.5^7 ≈ 0.078 < 0.1). Tunable via the module-level
   `REFINE_BUDGET_DECAY` and `MIN_USEFUL_BUDGET_SECONDS` constants.

2. **Mechanical signal-vs-noise classifier (§3.2).** Four rules in
   order: (a) empty/zero-magnitude → `noise`; (b) drift-fingerprint
   match → `instrument_drift`; (c) any of the four canonicalizer
   subclass signatures present → `signal`; (d) `coeff_variance > 0.5`
   → `signal`; (e) else → `noise` (or `unclassified` if calibration
   map is empty AND the shape's kind looks drift-related).

3. **Instrument-self-audit auto-trigger (§3.3).** Drift-class
   residuals can be passed to `record_meta_claim` to mint a CLAIM
   targeting the battery itself, not the original hypothesis. This is
   the systematic Penzias-Wilson move.

## Falsification paths from the proposal §5

The Residual primitive is itself killable. Four kill paths:

1. **Classifier kill.** If the 30-residual benchmark accuracy drops
   below 80% on any subsequent expansion, or any false-positive
   `signal` on known-noise appears, the classifier's value is gone
   and either (a) the heuristic threshold needs tuning, (b) the
   four-subclass taxonomy is wrong for this purpose, or (c) the
   primitive is unsalvageable. **Ship status: shipped at 100%; will
   re-run benchmark at every expansion.**

2. **Cost-budget kill.** If the doubling rule terminates
   Mercury-class chains too early — e.g., if Ramanujan-Hardy partition
   asymptotic refinement requires depth > 7 to find the next
   correction term — the doubling factor is wrong. **Mitigation: tune
   `REFINE_BUDGET_DECAY` upward (e.g., 0.6) or root budget (e.g., 30 s)
   to allow deeper chains while preserving exponential cost.**

3. **Storage-pollution kill.** If the `residuals` table grows by > 10×
   the rate of `claims` over a session, the substrate is over-capturing.
   **Mitigation:** add an eviction policy that archives `noise`-class
   residuals to cold storage after N days; only `signal` and `drift`
   residuals are kept hot.

4. **Discipline-erosion kill.** If, six months in, residual chains
   are routinely depth > 7 and consuming > 30% of compute without
   PROMOTE events, the budget rule is too lenient. **Mitigation:**
   tighten `REFINE_BUDGET_DECAY` to 0.4, add a hard depth cap of
   10 with a warning at 7.

If three of four kill paths fire on the proposed design in the first
month, roll the primitive back. That's the discipline.

## Postgres activation path

Apply migration 003:

```bash
psql -h <host> -U <user> -d prometheus_fire \
    -f sigma_kernel/migrations/003_create_residual_tables.sql
```

For prototype isolation:

```bash
psql -h <host> -U <user> -d prometheus_fire \
    -v schema=sigma_proto \
    -f sigma_kernel/migrations/003_create_residual_tables.sql
```

Then construct the extension with the same schema name:

```python
from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.residuals import ResidualExtension

kernel = SigmaKernel(backend="postgres")
ext = ResidualExtension(
    kernel,
    schema="sigma_proto",
    calibration_signatures=load_calibration_anchors(),
)
```

The Postgres adapter rewrites unqualified table names (`residuals` →
`sigma.residuals`) and `?` → `%s` automatically, same translation
pattern as `bind_eval.py`.

## Run the tests

```bash
pytest sigma_kernel/test_residuals.py -v
```

All 21 tests should pass; the 30-residual benchmark is the
load-bearing one (`test_composition_30_residual_benchmark_load_bearing`).
