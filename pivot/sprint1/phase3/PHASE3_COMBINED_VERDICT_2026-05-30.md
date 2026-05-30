# Phase 3.A + 3.B + 3.C — Combined verdict (ITER-57)

**Date:** 2026-05-30 (same day as Phase 3.0 FAIL + this combined retry)
**Verdict:** **Architectural redesign required.** Path C (counter-aware Layer 2 redesign) becomes priority. S1-S6 remain paused. Seam is provisionally sufficient.
**Harnesses:** `seam_sufficiency_audit.py` + `layer1_enrichment.py` + `real_residue_smoke.py`

---

## What the 2x2 matrix produced

The 2026-05-30 review predicted a 2x2 outcome matrix for (A: seam pass/fail) × (B: enrichment pass/fail). Ran both. The actual result:

```
                B PASS                   B FAIL
A PASS       resume S1            enrichment was            <-- WE ARE HERE
                                  not the issue;
                                  Layer 2 primitives
                                  redesign needed
A FAIL    seam dropped        architectural
          Layer-1 info        redesign needed
```

**(A PASS + B FAIL).** The seam is provisionally sufficient (Path A: raw doesn't beat seam — weak evidence of sufficiency). Enriching the ledger with 60 fresh real Layer-1 verdicts did NOT close the counter-baseline gap (Path B). The implication is that Layer 2's primitives as designed are structurally equivalent to per-plugin counters at the current data shape.

## Path A — seam-sufficiency audit (raw vs seam predictor)

```
n_train (chronological)       = 403 pairs
n_test                        = 174 pairs
seam-only accuracy            = 0.5000
raw accuracy                  = 0.4828
raw - seam                    = -0.0172
verdict                       = SEAM_SUFFICIENT (weak)
```

Honest reading: raw UNDERPERFORMED seam by 1.7 percentage points. Per the harness doc's own caveat, this is INCONCLUSIVE on seam sufficiency (raw could be losing to predictor overfitting, not because the seam is sufficient). Both predictors at ~50% accuracy on a 16-class problem (chance ~6.7%) — meaningful structure exists in both feature sets; raw didn't exploit additional info our naive majority predictor could use.

What this licenses: provisional treatment of the seam as sufficient under the predictor we tested. A richer predictor (e.g., per-feature decision tree) might find different signal. The decisive test would be a real downstream consumer (e.g., Layer 2 routing) winning more with raw than with seam.

## Path B — Layer-1 enrichment (60 fresh real verdicts)

```
G10 BOCPD x 5 hazard rates       -> 5 enriched rows
G23 bootstrap CI x 20 seeds      -> 20 enriched rows
G11 MC G-test x 20 seeds         -> 20 enriched rows
G02 WY x 5 seeds x 3 binaries    -> 15 enriched rows
                                    --------------
Total enriched rows              -> 60
```

Each row is a REAL detector run on the REAL Mossinghoff catalog (8596 non-cyclotomic entries) at a distinct parameter setting. Output written to `charon/agents/erebos/state/kill_ledger_enriched.jsonl` — separate from production state.

Per-detector kp diversity added:
- G10: `sharp_boundary_detected_bocpd` vs `smooth_decay_bocpd` (2 kps)
- G23: 3 of {`decay_consistent_with_1_over_N`, `error_term_does_not_decay_bootstrap`, `decay_faster_than_1_over_N_bootstrap`, `decay_slope_ci_straddles_boundary`}
- G11: `degree_minima_concentration_mc_significant` vs `flag_distribution_uniform_under_mc_null` (2 kps)
- G02: 6 kps (per-binary × promoted/rejected)

That's ~13 distinct rich kps vs the original ledger's ~22 (many of which were `*_pending`).

## Path C — Phase 3.0 smoke re-run with combined ledger

```
N_real_rows                          = 638 (570 production + 60 enriched - 1 dedup overhead)
N_shuffle_trials                     = 20
seed                                 = 1031

Substrate motif concentration        = 0.5591
Shuffled motif concentration (mean)  = 0.3988
Shuffled motif concentration (std)   = 0.0153
z-score                              = 10.4756 (was 9.80 on production-only)

Substrate motifs found               = 23 (was 17)
Substrate voids found                = 0  (was 0)
Distinct plugins                     = 16 (was 13)

Plugins where Layer 2 != counter     = 0 / 16   <-- KEY METRIC
Actionable routing deltas            = 0
```

**The headline number didn't budge.** The substrate's z-score improved (10.5 vs 9.8 — more structure detected), and motifs / plugins grew. But the actionable routing delta count remained zero. Layer 2's recommendations still match per-plugin majority on every plugin.

## What this combined verdict actually says

The naive interpretation — "Layer 2 fails on real data" — is incomplete. The more precise interpretation:

> **The motif extraction primitive (ITER-40), as designed, computes the SAME function as a per-plugin majority counter, by construction.** It groups rows by (plugin, kp) and counts. Per-plugin majority counter groups rows by plugin and computes most-common kp. The output is structurally identical when there's one dominant kp per plugin (which is the case in the real ledger, even after enrichment).

This is not a bug. It's a structural property of the primitive. The substrate's value claim — that Layer 2 produces decision-relevant signal counters cannot — requires Layer 2 primitives that consume MORE than 1-D (plugin, kp) tuples:

- **Cross-cell motifs.** Patterns spanning multiple (plugin, kp) cells. The current motif extractor finds NO cross-cell motifs because it's defined as a per-cell counter.
- **Domain transfer.** Real Mahler data has only ONE meaningful domain. To test cross-domain transfer, the substrate needs rich data in 2+ domains. (BSD MVP loader was supposed to provide this — paused per Phase 3.0.)
- **Temporal / sequence structure.** Rolling kp transitions. The chain motif extractor exists but the ledger isn't ordered to surface meaningful kp chains.
- **Higher-order tensor operations.** Null-space detection (ITER-42) IS designed for this but found ZERO voids on the enriched ledger — the bounding box is too sparse for voids to emerge.

## Honest restatement of the architectural claim

The Layer-1 + Seam + Layer-2 architecture claims that EXPLICIT failure geometry (Layer 2 primitives) outperforms IMPLICIT failure pressure (counters / random) at substrate-internal navigation tasks. After Phase 3.A + 3.B + 3.C:

- **Synthetic Sprint-1:** Layer 2 ≫ random ✓ (but ≈ counters, not tested)
- **Real production ledger:** Layer 2 ≫ random ✓, Layer 2 = counters ✗
- **Real production + 60 enriched rows:** Layer 2 ≫ random ✓, Layer 2 = counters ✗

The claim **as currently operationalized** is empirically false on real data, regardless of Layer-1 verdict richness. The primitives need redesign to produce signal counters can't replicate, OR the claim needs reframing.

## What the substrate must decide

This is bigger than the original Phase 3.0 FAIL. The verdict puts the substrate at a doctrinal crossroad:

### Option 1 — Reframe the claim

The substrate is not claiming Layer 2 produces decisions counters can't, but Layer 2 produces NAVIGABLE STRUCTURE (motifs / tensor / voids) that counters don't have access to as a representation. Counters output one recommendation per plugin; Layer 2 produces a tensor a human / model can READ. The value is in the queryability, not the routing.

This reframe is defensible but weaker than the original doctrine. It moves Layer 2 from "decision-improving" to "representation-enriching." The kill rule of Sprint-1 was about decision improvement.

### Option 2 — Redesign Layer 2 primitives

Build motif extractors that consume CROSS-CELL patterns: motifs of motifs, transitions between motifs, motif co-occurrence in time windows. These cannot collapse to per-plugin majority counters. The architecture's value claim survives but the implementation needs significant change.

### Option 3 — Accept the result and pause

The current architecture demonstrably does not pass the discriminating test the review designed. The doctrine's pre-committed kill rule (4+ Sprint-1 fails on the original protocol) was not triggered. The 2026-05-30 review's more discriminating test (counter-baseline on real data) was triggered. The architecture pauses for a deeper redesign before any further infrastructure work.

### Recommendation

**Option 2 + acknowledge Option 1.** The motif extractor (ITER-40) as a per-cell counter is the load-bearing limitation. A cross-cell motif primitive — "find pairs of motifs that co-occur in the same input_signature" — would by construction produce information counters can't (counters don't track motif co-occurrence). Build that primitive as ITER-58; re-run Phase 3.0 smoke; iterate.

If a redesigned motif primitive ALSO ties counters, Option 3 becomes mandatory. The doctrine has a hidden assumption (per `feedback_seam_sufficiency_audit`) that ITER-58 would test: that there is genuine cross-cell structure to find in real ledger residue at all.

## Doctrinal posture

Per `feedback_failure_metabolization_doctrine`: this is the doctrine's hardest moment. The single phrase says "optimization consumes failure; Prometheus metabolizes failure." Phase 3 produced a failure that the architecture cannot trivially metabolize — it falsifies the operationalized form of the doctrine's main claim. The substrate's choice now is whether the doctrine's claim survives a reformulation or whether the doctrine itself needs revision.

Per `feedback_take_a_stand`: the substrate takes the stand that Option 2 is the right next move. Build a cross-cell motif primitive. Re-test. If the redesigned primitive ALSO ties counters on real data, escalate to Option 3 and reopen the doctrine.

Per `feedback_counter_baseline_discriminator` (just added 2026-05-30): "if a Layer-2 primitive cannot beat counters on the same data, either the data doesn't have structure beyond what counters surface OR the primitive's design is sophisticated where simpler would work." Both are now real possibilities. Option 2 tests the second. Option 1 accepts the first.

---

## Sprint-1 + Phase 3 closing scoreboard

```
Sprint-1 (synthetic + structural)
  Verdict: 10/10 PASS (instrument-calibration, NOT architectural)

Phase 3.0 (single real-data smoke, counter baseline)
  Verdict: FAIL (0/13 actionable deltas vs counters)

Phase 3.A (seam-sufficiency audit)
  Verdict: provisionally SUFFICIENT (raw underperforms seam,
           predictor weakness can't be ruled out)

Phase 3.B (60 fresh real Layer-1 verdicts via parameter sweeps)
  Verdict: enrichment shipped, did not close the gap

Phase 3.C (smoke re-run with combined production + enriched)
  Verdict: still 0/16 actionable deltas vs counters
           z=10.48 vs shuffled (real structure exists,
           but it's the structure counters already see)

Overall architectural verdict: REDESIGN OPTION 2 REQUIRED
  before any infrastructure (S1-S6) work resumes.
```

---

**End Phase 3 combined verdict. ITER-57 closes. Next: ITER-58 — cross-cell motif primitive design + smoke retest.**
