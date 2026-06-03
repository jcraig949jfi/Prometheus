# Calibration v3 — VERDICT: the v2 corpus "signal" is selection-bias artifact

**Date:** 2026-06-03
**Author:** Techne
**Probes:** `theseus/scripts/calibration_v3_nonmutated.py` (all-gen + a1-only)
**Inputs:** v2 corpus sweep (`pivot/calibration_v2_corpus_sweep_2026-05-30.md`)
**Artifacts:** `pivot/calibration_v3_nonmutated_2026-06-03.md`,
`pivot/calibration_v3_nonmutated_a1_2026-06-03.md`

---

## TL;DR

v2 reported that ~18.5% of analyzed (invariant-pair × relation) groups show
an F2 content-aware contrast on the substrate's real corpus, while flagging
(its own caveats #2/#3) that most was likely selection bias. v3 ran the
decisive independent-null falsification. The result:

**The corpus "signal" is selection-bias artifact, in two compounding layers.
Under the only sampling mode with no selection bias — generator a1's uniform
independent `rng.choice` — the cross-catalog F2 contrast is ZERO (0 of 96
groups promote; max contrast 0.023, far below the 0.10 threshold). There is
no detectable knot×EC catalog coupling in this corpus.**

This is a clean PASS for the substrate's *calibration*, not a failure: F2
recovers PLANTED structure (synthetic Murasugi v0, EC-torsion v1) and reports
~zero where there is genuinely nothing to find. The substrate is not
hallucinating signal. The apparent corpus signal was an instrument reading the
generators' construction, which the independent-null probe correctly stripped.

---

## The two selection-bias layers v3 stripped

**Layer 1 — mutation inheritance.** A record with a `parent_record_id` was
produced by transforming an existing record (C2/C4/D2 K-mutators, etc.); its
(value_a, value_b) inherit the parent's selection. Excluding them:

- v2 analyzed **1,068** groups (≥50 all-record). Only **96** survive with ≥50
  *independently-sampled* records. ~91% of v2's group diversity is mutation-
  generated K-variants (`abs_diff_le_47`, `abs_diff_le_61`, …).
- v2's named *strongest residual*, `knot/trace_field_class abs_diff_le_0
  ec/torsion` (v2: 31.9% vs 7.1% null, n=1,694), is **100% mutation-derived**
  — 0 non-mutated records. It collapses entirely.

This confirms v2 caveat #3.

**Layer 2 — non-a1 generator selection/transform.** After excluding mutation,
61/96 groups still showed contrast up to 0.27 — but this is mechanically
impossible to read as coupling, because:

- a1 samples knot, EC, both invariants, and the relation by *independent
  uniform* `rng.choice` (`theseus/generators/a1_catalog_cross_product.py:158-164`).
  For independent sampling, observed hold rate **must** equal the random-
  repairing null in expectation.
- Yet the all-generator non-mutated groups showed `sub_hold` 22–40% against
  `null` frequently **0.00%** (e.g. `knot/three_genus abs_diff_le_3
  ec/conductor`: 25.5% vs 0% — `abs_diff ≤ 3` between a tiny genus and a large
  conductor is structurally near-impossible for random pairs).
- All 96 surviving groups carry a near-identical ~30% mutation fraction — the
  fingerprint of a single structured generation pipeline, not catalog structure.

The a1-only re-run isolates Layer 2:

```
                          all non-mutated gens     a1 only (uniform)
groups promoted (F2)      61 / 96   (63.5%)        0 / 96   (0%)
max contrast              0.274                    0.023
sub_hold vs null          22–40% vs ~0%            sub ≈ null everywhere
records with parent       (excluded)               0  (a1 never mutates)
```

a1-only top groups: `three_genus equal_mod_2 conductor` 51.1% vs 48.9%;
`three_genus divides rank` 66.0% vs 67.8%; `signature abs_diff_le_3 rank`
63.1% vs 64.6%. Every group: `sub_hold ≈ null`, contrast < 0.025. Exactly the
theory prediction for unbiased independent sampling.

---

## What this means

1. **No cross-catalog coupling in the corpus.** Under unbiased sampling, knot
   invariants and EC invariants are independent in this corpus. The relations
   that "held" did so by codomain structure (parity is ~50/50; `divides` into
   a small rank is common), not by coupling — and at exactly the null rate.

2. **F2's calibration is genuine.** It recovers planted relations (v0/v1) and
   reports ~zero on the unbiased real null. This is the signal-existence test
   GPT-5's review demanded, and F2 passes both directions.

3. **The 92-consecutive-0-promoted bandit streak is correct behavior, not a
   wall.** There is nothing to promote in the knot×EC region under honest
   scoring. The streak was the substrate refusing to promote artifacts. Per
   `feedback_gen_30_wall`, the response is NOT to deepen the menu in this
   region; it is generator-menu growth into regions that might carry coupling,
   or accepting this region as mapped-empty.

4. **Generator audit owed.** The Layer-2 inflation means several non-a1, non-
   mutation generators emit pairs whose `value_a`/`value_b` either (a) are
   selected toward holding, or (b) are operator-transformed so the *raw* values
   stored don't match the values the relation was evaluated on (v2 caveat #2).
   Either way, those generators' SHADOW verdicts are not comparable to a raw-
   value null. **Next probe:** per-generator `sub_hold` vs null on the 96
   groups, to name which generators inject the bias and decide whether their
   records belong in the content-aware corpus at all.

---

## Doctrinal accounting

- **Calibration discipline (charter §2):** the independent null ran BEFORE the
  v2 "~18% signal" framing escaped upward as a claim. It killed the headline.
- **`feedback_assume_wrong` / `feedback_false_profundity`:** a candidate signal
  killed; the kill is the output. The probe makes the next instrument sharper.
- **`feedback_counter_baseline_discriminator`:** the a1 uniform-sampling null is
  the counter-baseline the apparent signal had to beat. It did not.
- **`feedback_permutation_null`:** independent-pairing null mandatory for any
  coupling claim — applied, claim killed.
- **HARD-5 (domains are docstrings):** no bridge story. The finding is
  "operator/generator X produces contrast S; under unbiased sampling S→0."

**Honest claim:** F2 calibrates on synthetic planted structure and correctly
finds NO cross-catalog coupling in the substrate's knot×EC corpus under
unbiased sampling. v2's apparent corpus signal was generator selection bias in
two layers, both stripped by v3.
