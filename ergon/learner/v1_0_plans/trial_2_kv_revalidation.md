# v1.0 Plan — Trial 2 KillVector-Ranked Fitness Re-Validation

**Filed by:** Ergon (loop fire 5, 2026-05-07)
**Source ticket:** T-2026-05-06-E005 (P3-low; documented + BLOCKED-DEFERRED-V1.0)
**Status:** Plan only. No code changes for v0.5 / v0.5b / v0.5c. Implementation begins post-pitch when the v1.0 phase formally opens.

---

## 0. What this is

The original Trial 2 (v0.5 MVP) hit 47σ on all 4 acceptance criteria using **cell-fill-only fitness**: a genome won its archive cell if it filled a previously-empty cell, period. Within-cell ranking was implicit (first-to-fill wins, ties broken by `content_hash` for determinism).

**v8 design doc (W1.6) deferred a re-validation** under KillVector-ranked within-cell fitness: a genome wins its cell if its KillVector has a *smaller* L2 distance to the zero-vector than the current incumbent — i.e., the cell stores the genome whose substrate-PASS profile is closest to "all 4 falsifiers cleared." This is the substrate-grade fitness because it forces the archive to surface genomes that are *closest to passing the kill battery*, not just genomes that explored a previously-empty descriptor cell.

**The honest reason this is deferred:** the v0.5 Trial 2 result (47σ structural-over-uniform on cell-fill rate) might collapse below 1.5× under KillVector-ranked fitness. That would itself be an informative substrate-grade finding (the structural operator's edge is in cell-exploration, not in producing closer-to-passing genomes), but it requires running the experiment to find out.

## 1. Why now-not-now

**Now-not-now drivers:**
- v0.5 / v0.5b / v0.5c is in pitch-artifact mode (per James 2026-05-06 override). Risk-positive trial reruns are scoped out.
- LoRA at 50 steps × rank 8 is bit-identical to base (per fire 1+2 finding). Re-running Trial 2 under any fitness function while the LoRA path produces no measurable signal would just confirm the same flat result; the discriminating question requires LoRA hyperparam exploration that itself is v1.0-scoped.
- Substrate v2.2's KillVector v2 (+8 components: relativizes / naturalizes / local_global_gap / requires_unproven_conjecture / asymptotic_only / small_case_artifact / asymmetric_effort / interpretive_slack) lands in the joint sprint. The revalidation should ideally consume v2 KillVector, not v1.5's 12-component form — running on v1.5 would mean redoing under v2 later.

**Now-do drivers (none active for this ticket):**
- Substrate v2.2 KillVector v2 has shipped and is consumable.
- LoRA hyperparam exploration has identified a regime where LoRA produces non-trivial movement (i.e., the v0.5 finding "lora ≡ base" no longer holds).
- A v1.0 design pass has formally opened.

## 2. Implementation plan

### 2.1 Fitness function modification (`ergon/learner/archive.py`)

Current `MAPElitesArchive.submit(genome, cell, fitness)` accepts a fitness tuple `(battery_survival_count, band_concentration_tier, cost_amortized_score)` and uses lexicographic comparison.

New within-cell ranking:
1. Primary key: `kill_vector_l2_distance_to_zero` (smaller = better; closer-to-passing)
2. Secondary key: `battery_survival_count` (existing, larger = better)
3. Tertiary key: `band_concentration_tier` (existing, larger = better)
4. Tie-break: `content_hash` (deterministic; no numeric advantage either way)

The KillVector v2 L2 distance is computed across all components that have a numeric `margin` (some components like F1's p-value are deferred-margin per `KillVector` spec; those contribute 0 if `triggered=False`, ∞ if `triggered=True` and `margin=None`). Per-component normalization needed before L2 sum (see §2.3).

**Contract impact:** add `kill_vector_distance_to_zero(kv)` helper in `kill_vector.py` (new fn, additive); extend `FitnessTuple` with optional `kv_distance: Optional[float] = None` field (default None preserves prior behaviour for callers passing the old 3-tuple). Backwards-compat: existing trials run without this field route to the legacy lex order. **No existing-signature breakage.**

### 2.2 Trial 2 KV revalidation script (`ergon/learner/trials/trial_2_killvector_revalidation.py`)

Same protocol as v0.5 Trial 2 (5 seeds × 1K episodes × all 5+ operator classes), but:
- `MAPElitesArchive` configured with `use_kv_distance_ranking=True` (new opt-in flag; default False preserves v0.5 behaviour)
- KillVector emitted natively per episode (via the BindEvalKernelV2 path that already lands by v1.0)
- Synthetic-null gate (W4.0) re-passes under the new fitness: train on shuffled labels, verify gate doesn't fire on artifacts
- Acceptance criteria revisited:
  - **Primary:** structural ≥1.5× uniform on signal-class-residual rate (same as v0.5; just different fitness for cell occupancy)
  - **Secondary:** absolute cell fill ≥20-30% (v8 spec; was 13.7% under cell-fill-only, expect higher because KV-ranking lets multiple-genomes-per-cell evolve toward better margins)
  - **Tertiary:** no axis concentration >70% (descriptor non-degeneracy)

### 2.3 Per-component margin normalization

Components have heterogeneous units (`absolute`, `p_value`, `z_score`, `hamming`, `count_factors`). Naive L2 sum is meaningless. Use:
- Z-score normalize each margin against the empirical distribution from the existing 470K+ episode ledger
- Or use the published kill_vector_navigator's normalization (already validated for the deg14 ±5 step navigator recommendation)
- Document the normalization choice; regression-lock the resulting L2 distance values

### 2.4 Comparison to v0.5 result

Honest analysis:
- Did structural-vs-uniform multiplier hold (≥1.5×)?
  - Pass: KV-ranking fitness IS substrate-grade; v0.5 finding was robust
  - Fail: structural operator's edge is in exploration, not in passing-closer; substrate-grade finding requiring re-framing
- Did the absolute substrate-PASS rate change?
  - Higher: KV-ranking surfaces genomes the cell-fill-only fitness was hiding
  - Same: KV-ranking is a no-op on this corpus (cell-fill saturation already concentrated near-passing genomes)
  - Lower: a particular concern — would mean cell-fill-only was over-counting "passing" by surfacing first-to-fill regardless of margin

### 2.5 Time + compute estimate

- 5 seeds × 1K episodes ≈ same wall as v0.5 Trial 2 (~10-15 min on the existing engine)
- Plus the KV-distance computation overhead: estimated +20-30% per episode (one extra L2 sum)
- Total: ~15-20 min wall-clock for the full run; results parity with the v0.5 protocol

## 3. What this plan does NOT promise

- A specific direction for the result. The honest expected outcome is **either** (a) structural ≥1.5× holds under stricter fitness — confirms v0.5 finding — **or** (b) it collapses, surfacing that the structural operator's edge is in cell-exploration not margin improvement. Both are pitch-positive substrate-grade findings.
- A timeline for v1.0 itself. This plan is filed against v1.0 / post-pitch when the corresponding phase opens.
- Adoption of KV-distance ranking as the default fitness. Even if v1.0 confirms the finding, callers may explicitly want cell-fill-only for exploration runs (where coverage matters more than margin).

## 4. Coordination dependencies

| Dependency | Owner | When needed |
|------------|-------|-------------|
| KillVector v2 (+8 components) shipped + emitting natively | Techne (substrate v2.2 §7) | Tier 1 P1, ~Day 6-7 of joint sprint |
| Per-component normalization spec | Techne / Ergon joint | Before script ships |
| Synthetic-null gate (W4.0 calibrated H0 from E006) consumed | Ergon (already DONE) | Already available |
| LoRA hyperparam exploration showing non-trivial signal | Ergon v1.0 phase | Pre-requisite for the LoRA-arm of the trial; the engine-only arm can run earlier |

## 5. Pre-registration

Per substrate-grade discipline (`feedback_aporia_review_2026_05_04.md` / `feedback_assume_wrong.md`): the prediction is registered now, before implementation:

> **Pre-registered hypothesis:** structural-vs-uniform multiplier under KV-distance-ranked fitness is between 0.8× and 4× (i.e., either confirms the v0.5 finding within an order of magnitude, or modestly collapses). I do NOT predict 47σ; the v0.5 finding's effect size was inflated by the cell-fill-only metric capturing exploration, not margin quality.

Pre-registration prevents post-hoc "this is what I expected all along" rationalization (`feedback_narrative_resistance.md`).

---

*Filed by Ergon, loop fire 5, 2026-05-07. Status: BLOCKED-DEFERRED-V1.0 per E005 ticket spec. Re-activate when v1.0 phase opens.*
