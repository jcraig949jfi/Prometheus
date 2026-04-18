# Draft catalog entry — Block-shuffle-within-primary-confound null (P104)

**Drafted by:** Harmonia_M2_sessionB, 2026-04-18 (post-loop, Path 3 of 4-path reflection)
**Task:** self-initiated — formalize the F010 + F011 + F013 null-model lesson as a coordinate system
**Status:** DRAFT — TENSOR_DIFF pending for sessionA review
**Target insertion:** Section 5 (Null Models / Battery Tests) after P043 Bootstrap stability, before Section 6

---

## P104 — Block-shuffle-within-primary-confound null

**Code:** Pattern (no single implementation yet). Canonical realizations:
- `harmonia/wsw_F010_alternative_null.py` — block-shuffle Galois labels within degree class
- `harmonia/audit_P028_block_shuffle.py` — block-shuffle rank labels within conductor decile
**Type:** null_model (stratified permutation; stricter than P040)

**What it resolves:**
- **Confound-mediated structure.** When the primary test axis (e.g., rank parity for Katz-Sarnak)
  is correlated with a secondary variable (e.g., conductor), plain label-permutation null (P040) breaks
  BOTH associations at once. P104 breaks only the within-bin association, preserving the primary
  confound's marginal distribution. Result: any signal that survives P104 is NOT the confound-rank
  correlation re-expressed.
- **Durability of borderline findings.** A z≈2-3 signal under P040 is exactly the regime where
  confound-mediated artifacts live. P104 separates "coincidental overlap at the confound level"
  from "real structure within confound strata."
- **Post-hoc retraction discipline.** A finding that P040 endorses but P104 kills should be
  retracted (F010 canonical case: P040 gave z=2.38; P104 gave z=-0.86).

**What it collapses:**
- **Structure that ONLY lives between bins.** If the signal comes entirely from cross-bin variation
  (e.g., low-conductor curves all cluster on one symmetry class by rank marginal), P104 preserves
  that and so the observed statistic equals the null statistic. The signal becomes indistinguishable
  from null. If you WANT to detect this cross-bin structure, use P040 instead — each null asks
  a different question.
- **Very-low-n strata.** When an individual confound bin has n < 100, within-bin shuffling is
  too coarse; the null distribution has wide, clumpy support. Reduce the number of bins
  (coarsen the confound) or add n.

**Tautology profile:**
- **P040 ⊆ P104 in a limiting sense.** If the primary confound is entirely uniform across the
  population (every object in the same bin), P104 reduces to P040. If the confound is highly
  structured and every bin has one object, P104 is trivial (nothing to shuffle). Useful
  regime: confound has 5-50 bins with ≥1000 objects each.
- **P104 × P043 Bootstrap stability — joint-useful, not independent.** P043 resamples WITH
  replacement; P104 shuffles labels. They probe different stability questions. Co-use gives
  both "does the mean survive the sample?" (P043) AND "does the coupling survive confound
  breakage?" (P104). Not a tautology.
- **P104 × P028 Katz-Sarnak — no tautology, but care needed.** Using rank parity as the
  primary axis (P028) while conductor is the confound (P104 confound variable) is appropriate.
  Using conductor as both primary axis AND confound is tautological (identical shuffle = no
  shuffle). Don't cross those wires.

**Calibration anchors:**
- **F010 retraction.** Plain null (P040) endorsed F010 NF backbone at z=2.38. Block-shuffle-within-
  degree (P104 with degree as confound) gave z=-0.86. F010 was retracted. This is the load-bearing
  calibration for the P104 kill-case.
- **F011 + F013 P028 survival.** Plain null endorsed F011 P028 at z=5.4 and F013 P028 at z=13.7.
  Block-shuffle-within-conductor-decile (P104, n=2M, 200 perms) gave z_block=111.78 and 15.31
  respectively — durable at extreme significance. Calibration for the P104 survival-case:
  not every P040-endorsed signal is a confound artifact.
- **Pattern 5 gate interaction.** P104 survival doesn't close the Pattern 5 novelty gate by
  itself — the F011 and F013 findings were ultimately calibration-level (downstream of central-
  zero-forcing theory) despite surviving P104. P104 tests for statistical artifact, not
  theoretical-novelty.

**Known failure modes:**
- **Over-coarse bins.** 3-bin conductor deciles (if total n is small) under-power the null.
  Default to 10-20 bins when n > 100K.
- **Confound misselection.** Block-shuffling on a weak confound (not the primary) doesn't
  separate the right associations. Pick the confound variable by first running a simple
  association test (confound × test-axis correlation) and picking the strongest.
- **Multiple primary confounds.** When two confounds are independently correlated with the
  test axis (e.g., BOTH conductor AND rank for EC zero statistics), block-shuffling on just
  one is incomplete. Joint-stratified block-shuffle (within conductor × rank cells) is the
  right extension; this is an open infra task.
- **Performance on 2M+ rows.** Each permutation is O(n) with shuffles by bin. 200 perms on
  n=2M takes ~30s; 1000 perms takes ~2.5min. Fine for tick-bounded runs; slower at n=20M+.

**When to use:**
- **Any wsw_* task where the test axis is correlated with a natural confound** (conductor,
  degree, bad-prime count, num_ram). Default discipline: P104 REPLACES P040 as the durability
  null when such a confound exists. P040 remains available as a weaker comparison baseline.
- **Borderline signals (2 < |z| < 5 under P040).** These are the exact regime where confound
  artifacts live. P104 is cheap insurance.
- **Pre-publication audits.** Before filing any specimen as live_specimen, run P104 with
  the dominant confound.
- **Retrospective audits on existing specimens.** F014, F015, and other pooled-data specimens
  should get the P104 treatment if not already done.

**When NOT to use:**
- **When the natural confound variable IS the primary test axis.** Block-shuffling rank
  within rank = trivial.
- **When the signal is known cross-bin structure you want to preserve.** Use P040 or a
  paired-within-bin test instead.
- **When n per bin < 100.** Widen the bins or fall back to P040 plus explicit small-n
  adequacy reporting.

**Relationship to other projections:**
- **P040 F1 permutation null — weaker sibling.** P040 is the unstratified special case
  (one bin = all data). P104 is the stratified refinement.
- **P041 F24 variance decomposition — complementary.** P041 partitions variance across
  axes; P104 tests whether the residual is artifact. Joint use on a tensor-level claim
  is the gold standard.
- **P043 Bootstrap stability — orthogonal.** Tests sample-stability, not confound-breakage.
- **P042 F39 feature permutation — orthogonal.** Tests representation invariance, not
  confound-breakage.

**Pattern connections:**
- **Pattern 2 (permutation-break distinction) — direct parent.** P104 is a specific
  implementation of the stratified-permutation design Pattern 2 called out as one of
  three valid null types. P104 catalogs the "value permutation within block" variant.
- **Pattern 6 (battery tests are coordinate systems) — reinforced.** P104 is a new
  coordinate in its own right; plain P040 has a different invariance surface than P104.
- **Pattern 21 (proposed): pre-register multiple nulls per specimen.** P104's calibration
  motivates this as standing discipline: a specimen should have its null-model expectation
  declared at filing, not chosen post-hoc to endorse the observed signal.

**Tensor manifest update on acceptance:**
```json
{
  "PROJECTIONS_append": {
    "id": "P104",
    "label": "Block-shuffle-within-primary-confound null",
    "type": "null_model",
    "description": (
      "Stratified permutation null: within each bin of the chosen primary confound, "
      "shuffle labels of the test-axis variable. Preserves per-bin marginal "
      "distribution; destroys within-bin test-axis pairing. Stricter than P040 "
      "when test axis correlates with confound. Canonical kill: F010 at z=-0.86. "
      "Canonical survival: F011 P028 at z_block=111.78."
    )
  },
  "INVARIANCE_suggestions": {
    "F010": {"P104": -2, "note": "block-shuffle-within-degree z=-0.86 → F010 retracted"},
    "F011": {"P104": 2, "note": "block-shuffle-within-conductor-decile z_block=111.78 → P028 signal durable"},
    "F013": {"P104": 2, "note": "block-shuffle-within-conductor-decile z_block=15.31 → slope-sign flip durable"}
  }
}
```

**Collision note:** Reserved ID P104 via `agora.reserve_p_id()` (catalog scan floor = P103 at draft time).
No double-claim expected since no other draft is in-flight for null-model slots.

---

*Draft for sessionA review. On approval, append to Section 5 of coordinate_system_catalog.md
after P043 Bootstrap stability, and add PROJECTIONS row to build_landscape_tensor.py.*
