# Generator #6 — Pattern-Class Auto-Sweeps (Mandatory Filter)

**Status:** Tier 1 (low infra, days). **This is the non-negotiable companion to every other generator.**
**Role:** Filter.
**Qualification:** Harmonia session with access to the symbol registry and ingestion path.
**Estimated effort:** 3–5 ticks for initial implementation; maintenance as new patterns promoted.

---

## Why this exists

Running producers without automated epistemic discipline is an F043 factory. Pattern 30 (algebraic coupling) caught one catastrophic failure only because a human reviewer read the specimen description; the substrate itself had no gate. As the probe count scales (via Map-Elites, cross-domain transfer, literature-diff, composition enumeration), human review does not scale. The filter has to.

This generator wires three patterns into the ingestion path as automated sweeps:

- **Pattern 30** — algebraic-identity coupling detection
- **Pattern 20** — pooled-vs-stratified artifact detection
- **Pattern 19** — stale / irreproducible prior-measurement detection

Every new SIGNATURE passes all three before landing in the tensor. CLEAR / WARN / BLOCK.

---

## Infrastructure to build

### Sweep 1 — Pattern 30 (algebraic-coupling checker)

**Input:** the two variables `X` and `Y` of any correlation / regression test, expressed as symbolic definitions (their algebraic lineage).

**Logic:**

1. Parse the symbolic definitions. Extract the set of atomic quantities on each side.
2. Check overlap. If `X` appears (possibly under log / power / shift) as a term or factor inside `Y`'s definition, flag.
3. Classify severity per Pattern 30 levels 0–4:
   - Level 0: no overlap → CLEAR
   - Level 1: weak algebraic dependence (one term, small coefficient) → WARN
   - Level 2: shared variable with non-trivial coefficient → BLOCK unless claim is phrased as "algebraic observation"
   - Level 3: rearrangement of a known identity → BLOCK, retract if already landed
   - Level 4: exact functional identity → BLOCK, reclassify as calibration-tier only

**Implementation path:** `harmonia/sweeps/pattern_30.py`. Uses `sympy` for symbolic manipulation. Each F-ID's description carries (or adds) an `algebraic_lineage` block declaring how the measured quantity is defined in terms of atomic fields.

### Sweep 2 — Pattern 20 (pooled-vs-stratified)

**Input:** any SIGNATURE reporting a pooled statistic without a stratified companion.

**Logic:**

1. Identify the obvious stratification axes for the dataset (conductor decile, rank, num_bad_primes, torsion, CM, ...).
2. For each, automatically compute the statistic stratified.
3. Report the pooled-vs-stratified divergence ratio and sign-agreement.
4. If ratio > 1.2 OR sign-discordant: WARN + emit re-audit task.
5. If sign uniform and ratio < 1.2: CLEAR.
6. If stratum sample sizes too small (n < 100 per stratum): FLAG_INCONCLUSIVE, don't block but require n-scale re-run.

**Implementation path:** `harmonia/sweeps/pattern_20.py`.

### Sweep 3 — Pattern 19 (stale measurement)

**Input:** any SIGNATURE that claims to re-measure an F-ID already in the tensor.

**Logic:**

1. Look up the F-ID's last-recorded SIGNATURE (original n, original scorer, original preprocessing).
2. If new n > 3× original n AND new effect size differs by > 3× OR sign-flipped: FLAG — stale original.
3. Write a `provenance_delta` block: what changed (n, scorer, preprocessing, subset).
4. If delta ≥ 3×: do not silently overwrite; require conductor annotation before tensor update.

**Implementation path:** `harmonia/sweeps/pattern_19.py`.

---

## Process

1. Implement the three sweeps as pure computation symbols (per `long_term_architecture.md §2.1`).
2. Wire them into the ingestion path: `agora/tensor/push.py` and `agora/register_specimen.py` call each sweep before committing.
3. Each sweep emits `{verdict: CLEAR|WARN|BLOCK, rationale: <text>, raised_by: <pattern>}`.
4. BLOCK halts the update and posts a `PATTERN_BLOCKED` message to `agora:harmonia_sync`. Human conductor review required to override.
5. WARN lets the update land but annotates the cell with a `sweep_warnings` block.
6. CLEAR passes through.

---

## Outputs

- `harmonia/sweeps/pattern_{30,20,19}.py` — three pure-computation sweep implementations.
- `harmonia/sweeps/runner.py` — orchestrator that runs all three on a SIGNATURE.
- Ingestion-path wiring in `agora/tensor/push.py` and `agora/register_specimen.py`.
- `harmonia/memory/sweep_results_log.md` — append-only record of every sweep verdict (for retrospective audit of filter calibration).
- Promotion of each sweep as a versioned `computation` symbol once the symbol type ships.

---

## Epistemic discipline

1. **Filters can themselves be miscalibrated.** The filter's false-positive rate needs monitoring. Every quarter, a conductor-initiated audit samples ~20 BLOCKED / WARNED cells and checks whether the block was correct. Mis-blocks are logged and the sweep rules adjusted.
2. **The sweep codebase is a load-bearing computation symbol.** It goes through the same VERSIONING discipline as any other promoted symbol. v1 is immutable once shipped; corrections promote v2.
3. **WARN vs BLOCK is a judgment.** Start conservative: Level 2 is BLOCK, Level 1 is WARN, ratio > 2× is BLOCK on Pattern 20. Tune after a month of operation.
4. **Override path must exist.** The conductor can override a BLOCK after review; override is recorded with justification. No silent bypasses.

---

## Acceptance criteria

- [ ] Three sweep implementations shipped, with tests.
- [ ] Ingestion-path integration committed; a SIGNATURE that would have been F043 gets BLOCKED in the test.
- [ ] `sweep_results_log.md` with first batch of retrospective sweeps on all existing +1 and +2 cells (baseline calibration — expect ~2–3 WARN, ≤ 1 BLOCK).
- [ ] Override mechanism + justification protocol documented.
- [ ] Commit cites this spec.

---

## Composes with

- **Every other generator.** Mandatory companion. Every producer's output passes through this filter.
- **#2 null-family** — Pattern 21 discordance check composes with these sweeps: a discordant family vector is a fourth pattern worth sweeping.
- **External review** — third external-review round was the first pass of this filter done by a human. #6 is the internalization of that role.

---

## Claim instructions (paste-ready)

> Claim `gen_06_pattern_sweeps_seed`. Implement Pattern 30, 20, 19 sweeps + runner + ingestion-path wiring per `docs/prompts/gen_06_pattern_autosweeps.md`. Retrospective-sweep all existing +1/+2 cells. Commit sweep modules + `sweep_results_log.md`. Post `WORK_COMPLETE` with block/warn/clear counts on retrospective batch.

---

## Version

- **v1.0** — 2026-04-20 — initial spec from generator pipeline v1.0. Non-negotiable companion declared.
