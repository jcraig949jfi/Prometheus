# Generator #1 — Map-Elites on Probes (Quality-Diversity Meta-Allocator)

**Status:** Tier 2 (medium infra, weeks). **Blocked on #2 null-family live + #6 pattern auto-sweeps live + ≥ 50 probes in the populated corpus.**
**Role:** Meta-allocator — allocates attention across the producer generators.
**Qualification:** Harmonia session with tensor-read access + Agora queue-write access + familiarity with the symbol registry and `harmonia/memory/coordinate_system_catalog.md`.
**Estimated effort:** 4–6 ticks for first end-to-end pass (behavior-descriptor design + grid + first elite set); ongoing as corpus grows.

---

## Why this exists

Every other producer (#3, #5, #7, #9, #10, #11) emits probes into the queue without knowing what the *other* producers just emitted. Left alone, the queue drifts toward the cheapest-to-generate shapes — overwhelmingly cross-domain transfers and attention-replays against the same handful of well-resolved axis classes. A corpus biased that way concentrates compute on a small behavioral region of probe-space and leaves most of the landscape unprobed.

Map-Elites (Mouret & Clune, 2015) is the appropriate instrument. It grids probe-space by **behavior descriptors** — what the probe *does*, not what it *is* — and keeps only the highest-quality probe in each behavior cell. The grid as a whole becomes the elite frontier. Allocation then works by asking: *which behavior cells are unoccupied or occupied by weak elites?* Producers get routed to fill those cells.

**The load-bearing insight:** probe-space is enormous but behavior-space is small. Two probes with wildly different surface form can occupy the same behavior cell (same axis class, same stratifier class, same domain, same null-family survival profile); the grid collapses that redundancy. Two probes that look surface-similar (e.g., both correlation tests against conductor decile) can live in very different cells if one resolves a feature and one doesn't; the grid preserves that distinction.

This generator does not emit probes directly. It reads the populated corpus, classifies every probe into a behavior cell, retains the elite per cell, and **re-weights the priorities of tasks already on the queue** (and emits targeted fill-requests to producers for empty cells). It is the feedback edge in the pipeline DAG.

---

## Inputs

- **Tensor (Redis mirror):** `agora.tensor.reconstruct_matrix` for the full cell state; `feature_meta(F)` and `projection_meta(P)` for per-cell descriptors.
- **Specimen registry (Postgres):** `signals.specimens` for per-probe outcome records (n_specimens, runtime, null-family verdict).
- **Symbol registry:** every probe dereferences to a composition of promoted symbols (dataset × operator × null). The composition IS the probe's identity.
- **Agora work_queue:** current pending-task set, with their priorities and emitting-generator labels.
- **Null-family results (from #2):** `SIGNATURE@v2.null_family_result` is the quality-score substrate.
- **Pattern sweep log (from #6):** `harmonia/memory/sweep_results_log.md` records which probes passed/warned/blocked. A BLOCKED probe is ineligible for the elite frontier regardless of z-score.

---

## Algorithm / first-pass procedure

### Phase 1 — define the behavior-descriptor space

The grid's axes are not the tensor's axes. They describe *behavioral* properties of a probe. First-pass axes (each discretized to 3–6 bins):

| Axis | Bins | Source |
|---|---|---|
| `axis_class` | {family, magnitude, symmetry, arithmetic, spectral, moment, operator} | P-ID's `axis_class` field in `coordinate_system_catalog.md` |
| `claim_class` | {1, 2, 3, 4, 5} per `null_protocol_v1.md` | SIGNATURE's claim_class |
| `domain` | {D_EC, D_NF, D_MF, D_ARTIN, D_G2C, D_KNOTS, D_L, D_HMF, other} | `domain_catalog.md` |
| `stratifier_class` | {none, marginal, 2-way, nested, continuous-binned} | SIGNATURE's stratifier spec |
| `null_family_coverage` | {1/4, 2/4, 3/4, 4/4 applicable nulls at z ≥ 3} | `null_family_result` verdict |
| `runtime_decile` | {0–3, 4–6, 7–9} | empirical runtime from specimen record |

First-pass grid cardinality: 7 × 5 × 9 × 5 × 4 × 3 ≈ 19K cells. Sparsity is expected and informative.

**Design discipline:** behavior descriptors must be *computable from probe metadata alone*, not from its outcome. Otherwise the grid is leaky — a probe moves cells post-hoc based on its result, and the elite frontier becomes an overfit of the corpus. The sole exception is `null_family_coverage`, which is a coarse post-hoc bin on outcome; this is defensible because it captures behavioral robustness, not effect size. Document the exception in the spec.

### Phase 2 — quality scorer

Per-cell quality of a probe is the tuple (sorted lexicographically for elite comparison):

1. **Validity gate (hard filter):** #6 sweep verdict ∈ {CLEAR, WARN}. BLOCKED probes ineligible.
2. **Null-family survival depth:** number of family-applicable nulls survived at z ≥ 3.
3. **Max |z| across family** (only used to break ties among equal-survival probes).
4. **Inverse runtime** (cheaper elite preferred if all else tied — incentivizes cheap probes).
5. **Recency** (newer preferred on exact tie — prevents elite ossification).

No single scalar score. The tuple is explicit to match the falsification-first epistemology: we do not want a quality metric that can be optimized by a probe with a single huge z and no null-family coverage.

### Phase 3 — grid population

1. Enumerate every cell in the tensor + every specimen in the registry that has a `SIGNATURE@v2`.
2. Assign each to its behavior cell via the descriptor functions.
3. For each occupied grid cell, retain the elite per the quality tuple.
4. Emit: `harmonia/memory/map_elites_grid.json` — `{cell_coord: {elite_probe_id, quality_tuple, occupancy_count}}`.

### Phase 4 — allocation signals

Three signals feed back to producers:

**Signal A — empty-cell fill requests.** For each occupied-neighbor cell that has an empty neighbor along exactly one axis, emit a `fill_request` task on Agora:

```python
{
    "task_id": f"mapelites_fill_{cell_coord_hash}_{yyyymmdd}",
    "type": "map_elites_fill",
    "target_cell": {"axis_class": "moment", "claim_class": 3, ...},
    "adjacent_elite": "<probe_id>",
    "qualification": "any_producer",
    "priority": -1.0,
    "notes": "Adjacent cell filled; this cell empty. Suggested adaptation: see target_cell descriptors.",
}
```

Adjacency is measured only along *one* axis — empty cells at large Hamming distance from any elite are beyond the frontier and not yet actionable.

**Signal B — re-weighting of pending tasks.** For each task already on `agora:work_queue`, compute its *predicted* behavior cell from its metadata. Adjust its priority:

- If predicted cell is empty: boost priority by `-0.5`.
- If predicted cell already has a high-quality elite (3/4 or 4/4 null-family): demote priority by `+0.5`.
- Otherwise unchanged.

Re-weighting runs on a cadence (e.g., hourly cron), not per-task, to avoid queue thrash.

**Signal C — producer-specific feedback.** For each producer generator, compute its *cell-fill efficiency*: (new elite cells opened by its outputs) / (tasks it emitted). Publish to `harmonia/memory/producer_efficiency.md`. Producers with consistently low efficiency get their global budget downscaled in the next allocation tick; this is a soft recommendation to the conductor, not an automatic budget change.

### Phase 5 — re-run cadence

Full re-population runs on tensor-update trigger OR weekly cron (whichever first). Allocation signals refresh same cadence.

---

## Discipline: MNAR random-sample quota floor (sessionE amendment, 2026-04-21)

**Load-bearing discipline.** The meta-allocator treats a 20% quota of every tick's emitted `fill_request` budget as a **uniformly-drawn random sample** across the (F × P) tensor lattice — **not** drawn from the adjacency logic of Signal A. The quota is a **floor, not a tunable knob**: the percentage floors at 20% per tick; skipped random draws roll forward to the next tick, never drop.

**Why this is in the spec.** The wave-2 external review (see `decisions_for_james.md` [2026-04-19]) established that the tensor's density pattern is shaped by researcher attention, not random sampling — a Missing-Not-At-Random (MNAR) bias that invalidates every aggregate claim across cells until corrected. Map-Elites on its own cannot correct this: adjacency-driven fill is, by construction, a continuation of the heuristic-concentrated pattern, because it only fills cells *adjacent to an existing elite*. Without a random-sample floor, gen_01 compounds the MNAR bias rather than measuring it.

**What the quota buys.** The ratio of random-cell landing rates (cells that resolve to a +1 / +2 signal) to heuristic-cell landing rates IS the selection-bias correction factor. Once measured across a few re-run cadences, aggregate tensor reasoning currently forbidden by the review re-opens with a defensible adjustment. The quota converts MNAR from a **blind spot** into a **measurable**.

### Spec delta against Phase 4

Add a fourth allocation signal alongside A / B / C:

**Signal D — MNAR random-sample quota (FLOOR, non-negotiable).** Each re-run of Phase 4 emits ≥ `0.20 × total_emitted_tasks_this_tick` tasks of type `map_elites_random_draw`. The target cells are chosen by uniform sampling across the (F × P) lattice, **excluding** cells already occupied by a valid elite (so the quota populates unexplored / under-explored regions rather than redundantly testing occupied ones).

```python
{
    "task_id": f"mapelites_random_{cell_coord_hash}_{yyyymmdd}",
    "type": "map_elites_random_draw",
    "target_cell": {"F": "F0XX", "P": "P0YY"},
    "drawn_by": "uniform_lattice_sampler_v1",
    "qualification": "any_producer",
    "priority": -1.2,  # higher than Signal A (-1.0) to ensure the floor lands
    "notes": "MNAR random-quota floor. Do NOT substitute an adjacency draw — this cell was drawn uniformly and is the calibration sample for the selection-bias correction factor.",
}
```

### Null-protocol routing (non-optional)

A uniformly-drawn (F × P) cell inherits the claim-class of its feature per `null_protocol_v1.md` — the random sampler must dispatch to the correct null per claim class, not run one null-of-record everywhere. Running every random draw under `NULL_BSWCD@v2` with a default stratifier recreates the single-null-usage problem the wave-2 review caught. The fill-request payload carries `target_F.claim_class` so the downstream producer can select the right null-family coverage (see `SIGNATURE@v2.null_family_result`).

### Measurable deliverable

The deliverable of the quota is the **ratio**, not a density increase:

```
R_mnar = P(signal | random_draw) / P(signal | heuristic_draw)
```

Report R_mnar monthly in `harmonia/memory/mnar_calibration_log.md` with confidence intervals. Track its drift: if R_mnar stabilizes at some value `r* < 1`, the tensor's apparent density overstates its real signal density by a factor of `1/r*`, and aggregate claims apply that correction.

**Reward-signal-capture guard.** The quota's success is measured by R_mnar being **measurable**, not by the tensor getting **denser**. A successful tick in which the 20% random draws return *zero* new elites is a *successful measurement of R_mnar near zero for that region* — a real finding, not a failure. The temptation to abandon the quota when it "wastes compute" is the capture failure mode; the wave-2 review's standing critique is load-bearing and the quota is the fix.

### Acceptance-criteria delta

Add to the acceptance list below:

- [ ] Signal D random-draw emitter shipped; unit test verifies ≥ 20% of emitted tasks per tick are of type `map_elites_random_draw` with uniformly-drawn `target_cell` coordinates.
- [ ] Null-routing dispatcher wired so each random draw carries the correct `claim_class` and default stratifier for its F's claim class.
- [ ] First R_mnar calibration run published in `mnar_calibration_log.md` after ≥ 50 random-draw completions.

### Provenance

Provocation #1 in `harmonia/memory/provocations.md` (Harmonia_M2_sessionE calibration, 2026-04-20). Status on promotion of this spec delta: **open → in-discussion → pinned in gen_01 canonical spec**. Keep the provocations entry Open until R_mnar first publishes; then update its Status to `tried:<outcome>` per the provocations template.

---

## Output schema

### Grid state
`harmonia/memory/map_elites_grid.json`:

```json
{
  "version": "v1.0",
  "computed_at": "2026-04-20T18:00Z",
  "grid_axes": ["axis_class", "claim_class", "domain", "stratifier_class", "null_family_coverage", "runtime_decile"],
  "bin_spec": {
    "axis_class": ["family", "magnitude", "symmetry", "arithmetic", "spectral", "moment", "operator"],
    "claim_class": [1, 2, 3, 4, 5],
    "...": "..."
  },
  "cells": {
    "family|2|D_EC|marginal|4_of_4|0-3": {
      "elite_probe_id": "F011:P028:NULL_BSWCD@v2",
      "quality_tuple": [true, 4, 111.78, 0.8, "2026-04-17"],
      "occupancy_count": 3,
      "competitors": ["F011:P020:NULL_BSWCD@v2", "F011:P007:NULL_PLAIN@v1"]
    }
    // ...
  },
  "empty_adjacent_cells": 312,
  "summary": {
    "total_cells": 18900,
    "occupied": 47,
    "frontier_adjacent_empty": 312,
    "occupied_with_4_of_4_null_family": 3
  }
}
```

### Fill-request task payload (posted to `agora:work_queue`)

```python
{
    "task_id": "mapelites_fill_<hash>_<yyyymmdd>",
    "type": "map_elites_fill",
    "target_cell": {"axis_class": "...", "claim_class": N, ...},
    "adjacent_elite_probe_id": "F???:P???:NULL_???",
    "suggested_producer": "gen_03" | "gen_05" | "gen_10" | "gen_11" | "any",
    "priority": -1.0,
    "qualification": "harmonia_session",
    "notes": "Map-Elites adjacency fill. See docs/prompts/gen_01_map_elites_on_probes.md §Phase 4.",
}
```

### Producer-efficiency report
`harmonia/memory/producer_efficiency.md` — table per generator: (tasks emitted, probes completed, new elite cells opened, cell-fill efficiency ratio, rolling 30-day trend).

---

## Acceptance criteria

- [ ] `harmonia/mapelites/` package shipped with descriptor functions, grid builder, quality scorer, allocation-signal emitter, and tests on a synthetic corpus of ≥ 20 probes.
- [ ] Behavior-descriptor spec committed; the "computable from metadata alone" invariant has an automated unit test that fails any descriptor touching outcome fields beyond the declared `null_family_coverage` exception.
- [ ] First grid population run against the live tensor + specimen registry produces `map_elites_grid.json` with ≥ 40 occupied cells.
- [ ] First allocation-signal run emits ≥ 10 `map_elites_fill` tasks and re-weights ≥ 30 pending queue tasks.
- [ ] `producer_efficiency.md` shipped with first-pass numbers for each producer generator that has ≥ 5 completed tasks.
- [ ] One worked example in `harmonia/memory/map_elites_log.md`: a fill-request task gets claimed, produces a probe, the probe lands in the intended cell (or explains why it didn't).
- [ ] False-frontier-rate monitoring scheme documented: quarterly audit samples ~20 elite cells and checks whether the elite's apparent quality holds on re-test. If > 20% degrade, the descriptor space is leaky — tighten.
- [ ] Commit cites this spec and the generator pipeline version.

---

## Known gotchas / epistemic hazards

1. **Behavior-descriptor leakage is the central failure mode.** If a descriptor is derivable from the probe's *outcome* (beyond the declared `null_family_coverage` exception), the grid silently overfits: probes shift cells post-hoc to match their result, and the elite frontier becomes a compressed ranking, not a behavior map. Every descriptor addition requires a written justification for why it is outcome-independent. The unit test enforces the invariant; the written justification enforces the discipline.

2. **Elite ossification.** A grid cell with a strong early elite will deter subsequent probes from that cell, even if the subsequent probe would have been a *better* elite. Map-Elites' canonical solution (accept new probe iff quality strictly exceeds current elite) is appropriate here. The `recency` tiebreaker in the quality tuple is explicitly to prevent ties from hardening into permanent occupancy.

3. **Empty cell ≠ unreachable cell.** Most empty cells in the first-pass grid are empty because no producer generates probes with that combination of behavior descriptors (e.g., `claim_class=5 × domain=D_KNOTS` may have no viable probe under any known operator). Emitting fill-requests into unreachable cells floods the queue with no-op tasks. First-pass heuristic: only emit a fill-request if at least one *adjacent* cell along each descriptor axis is occupied. Refine with a per-axis reachability model in v2.

4. **Pattern 30 inheritance.** Every elite probe is a candidate input to gen_10's composition enumeration. If an elite probe has an undetected algebraic coupling (Pattern 30 level 2+), its descendants through composition inherit the coupling. Gen_06's Pattern 30 sweep must have run against every probe *before* it becomes elite. The validity gate (Phase 2, step 1) enforces this; skipping it will compound failures across the whole allocation cascade.

5. **Null-family-coverage as a quality axis is a compromise.** It is the only post-hoc outcome bin in the descriptor space. The justification is that survival robustness across null models is a *property of the probe's relationship to reality*, not a property of any single measurement. If this hazard materializes (e.g., elites cluster at `4_of_4` because that cell gets priority-boosted fill-requests, and the boost causes more probes to reach `4_of_4` through sheer sampling), demote `null_family_coverage` from a grid axis to a tiebreaker in the quality tuple and re-run the grid. Log the demotion in the version history.

6. **The meta-allocator can drift into self-reinforcement.** If Signal C (producer-efficiency) reshapes producer budgets and the reshaped budget changes which cells fill next, the allocator is now measuring its own echo. Detection: producer-efficiency scores should be stable under resampling of a held-out window of the corpus. If they drift by more than 30% between adjacent weeks, the allocator is chasing noise; widen the rolling window or freeze Signal C until the drift abates.

7. **Pattern 18 interaction.** Pattern 18 (uniform visibility across walked projections → axis class orphan) is a finding-level signal that a feature needs a *new* axis class. Map-Elites' grid may mark the covered cells as elite-occupied and de-prioritize further probes along those axes. This is wrong: Pattern 18 is explicitly saying *the existing axes are the problem*. Gen_11 (coordinate invention) is the correct producer to trigger on Pattern 18; the allocator must recognize a Pattern 18 F-ID and route budget to gen_11 rather than suppressing further probes on that row.

---

## Dependencies

### Generators that must land first

- **#2 null-family** — `SIGNATURE@v2.null_family_result` is the quality-score substrate. Without it, the quality tuple collapses to max |z|, which is exactly the single-null failure mode this generator is designed to avoid.
- **#6 pattern auto-sweeps** — the validity gate cannot function without automated sweep verdicts. Manual gating does not scale to a live allocator.
- **Tier 0 producers (#3, #5, #7)** — need ≥ 50 completed probes in the corpus before the grid has enough density to allocate over. Target: wait until the corpus has ≥ 50 probes spanning ≥ 4 domains and ≥ 3 claim classes.

### Symbols / protocols that must exist

- `SIGNATURE@v2` (from #2) — promoted.
- `NULL_PLAIN@v1`, `NULL_BOOT@v1`, `NULL_FRAME@v1`, `NULL_MODEL@v1` (from #2) — promoted.
- `coordinate_system_catalog.md` with `axis_class` field populated per P-ID (currently partially populated; completion is a dependency).
- `domain_catalog.md` (from #3 Phase 1) — promoted.
- `null_protocol_v1.md` claim-class taxonomy — already exists.
- `harmonia/memory/sweep_results_log.md` (from #6) — live.

### Infrastructure not yet assumed

- No new Redis streams required — reads existing `tensor:updates`.
- No new symbol types required — registers as a `computation` symbol once the type ships (same as gen_06, gen_10, gen_11).

---

## Tier and priority

- **Tier 2.** Blocked on Tier 1 (#2, #6) and on corpus density from Tier 0 producers.
- **Priority within Tier 2:** high, but after #4 (representation invariance) has shipped at least a proof-of-concept. Reason: #4's reparameterization results are an important behavior descriptor to add in gen_01 v2. Shipping gen_01 before #4 exists means the first grid's descriptor space will miss an axis we already know matters, and retrofitting a new grid axis invalidates elites.

Concretely: #2 and #6 live → #4 proof-of-concept → gen_01 v1. Then #4 full pass → gen_01 v2 (adds `representation_invariance_depth` descriptor).

---

## Composes with

- **#2 null-family** — hard dependency; provides quality substrate.
- **#6 pattern auto-sweeps** — hard dependency; provides validity gate.
- **All producers (#3, #5, #7, #9, #10, #11)** — allocator re-weights their emitted tasks and emits fill-requests they can claim.
- **#4 representation invariance** — post-ship, adds a behavior-descriptor axis.
- **#8 synthetic-data sensitivity** — an elite probe's `synthetic_sensitivity_score` (if present) could enter the quality tuple as a robustness tiebreaker; defer to v2.

---

## Claim instructions (paste-ready)

> Claim `gen_01_map_elites_seed` from Agora **only if**: (a) `gen_02_null_family_seed` has landed and ≥ 30 SIGNATURE@v2 records exist in the registry, (b) `gen_06_pattern_sweeps_seed` has landed and the sweep runner is wired into ingestion, (c) the tensor has ≥ 50 non-calibration cells spanning ≥ 4 domains and ≥ 3 claim classes. If any precondition is unmet, post `WORK_BLOCKED` on `agora:harmonia_sync` with the failing precondition and claim a precondition task instead. Otherwise: implement `harmonia/mapelites/` package + `map_elites_grid.json` + allocation signals per `docs/prompts/gen_01_map_elites_on_probes.md`. Commit grid + producer-efficiency report + one-worked-example log. Post `WORK_COMPLETE` with grid occupancy counts, fill-request task IDs, and top-5 producer efficiency scores.

---

## Version

- **v0.1 DRAFT** — 2026-04-20 — initial spec from generator pipeline v1.0. Marked DRAFT because (a) behavior-descriptor space is first-pass and will need a v2 pass after #4 ships, (b) the reachability heuristic in Phase 4 Signal A is a placeholder for a proper model, (c) the producer-efficiency feedback (Signal C) has a known self-reinforcement hazard that needs empirical monitoring before we trust it to shape budgets. First implementation's job is to teach us what breaks.
