# Phase 3.0 — Real-residue smoke test verdict (ITER-56)

**Date:** 2026-05-30
**Verdict:** **FAIL — pause BSD loader work; inspect seam sufficiency**
**Harness:** `charon/agents/erebos/sprint1/phase3/real_residue_smoke.py`

---

## Headline

> The substrate's motif concentration on real ledger data is 9.80σ above shuffled-label baseline (clear structure beyond noise), BUT produces ZERO actionable routing deltas vs the per-plugin counter baseline. Across all 13 plugins in the real ledger, Layer 2's motif-based recommendation EXACTLY matches the trivial per-plugin majority counter. The sophisticated apparatus detects no decision-relevant structure that counters miss.

This is the diagnostic the 2026-05-30 frontier review predicted. Per `feedback_counter_baseline_discriminator`: "a substrate that calibrates well against random baselines but fails against counter baselines has built sophisticated measurement apparatus without epistemic gain."

## Why this was the right gate to run first

Sprint-1 closed at 10/10 PASS on 2026-05-29 against synthetic data + shuffled-label nulls. The review correctly reframed that as instrument-calibration, not architectural validation, and recommended inserting a single real-data smoke test BEFORE the ~10-iteration BSD-loader path. That test cost one iteration. It surfaced what Sprint-1 could not.

If the substrate had cleared the counter-baseline check, the 10-iteration path would have been justified. It didn't. Pausing now saves ~9 iterations of misdirected work.

## Numbers

```
N_real_rows                            = 570 (from erebos + stygian ledgers)
N_shuffle_trials                       = 20
seed                                   = 1031

Substrate motif concentration          = 0.6190
Shuffled motif concentration (mean)    = 0.4558
Shuffled motif concentration (std)     = 0.0167
z-score (substrate vs shuffled)        = 9.8040

Substrate motifs found                 = 17 (at min_count=3)
Substrate voids found                  = 0
Distinct plugins                       = 13
Distinct kill_patterns                 = 22 (in real data)

Plugins where Layer 2 != counter       = 0 / 13
Actionable routing deltas              = 0
```

## Three honest readings

### Reading 1: real residue has structure but it's the structure counters already see

The 9.80σ z-score is not random noise. There is something in the real ledger that's not in shuffled labels. But the structure that IS there is exhaustively captured by "what kp does each plugin most often emit?" — a 13-row counter table. The motif extractor's output collapses to the same recommendations.

This is consistent with the doctrine's seam-sufficiency hidden assumption (per `feedback_seam_sufficiency_audit`). Layer 1's verdicts carry information; the seam encodes the most-frequent (plugin, kp) co-occurrences; Layer 2 reads those co-occurrences. Counters read those co-occurrences too. The information advantage was supposed to come from voids, cross-domain transfer, rank-expansion, motif chains — but the real ledger is too sparse / pending-heavy / single-domain to surface any of those.

### Reading 2: the substrate hasn't yet produced the Layer-1 verdicts Layer 2 was designed to navigate

Of 570 rows:
- 347 are Stygian-battery-attack rows; 327 have kp in {`stygian_hecate_meta_test_not_yet_implemented`, `stygian_no_loader_registered`} (infrastructure-pending, not verdicts).
- 215 are Erebos-emitted claims with `*_pending` kps (= awaiting Stygian).
- Only ~8 distinct REAL Layer-1 verdicts exist (kp != "*pending*" and != "*not_yet_implemented*").

Layer 2's primitives need rich (plugin, domain, invariant, kp) populated cells to navigate. The real ledger has nothing close. Null-space detection found ZERO voids — not because the substrate is dense, but because the populated cells are concentrated on a few (plugin, "pending") tuples that all behave the same.

The architecture is calibrated against a Layer 1 that doesn't yet produce the failure types it claims to consume.

### Reading 3: synthetic Sprint-1 told the substrate something about itself but not about the world

10/10 PASS on synthetic data proves the primitives WORK when handed structure to find. The Phase 3.0 verdict says: when handed REAL substrate output, the primitives produce no decision-relevant signal beyond counters.

The gap is the gap between "the apparatus measures what it was built to measure" and "the apparatus measures something useful about reality."

## What this verdict licenses

- The 2026-05-30 review's central reframe is empirically vindicated. Sprint-1 was instrument-calibration. Phase 3.0 is the first architectural test.
- The BSD MVP loader work (S1) is paused. Building MORE Layer-1 surface area before the existing surface produces Layer-2-navigable residue is misdirected effort.
- The Tier 1 sequencing in `pivot/STATE_AND_NEXT_STEPS_2026-05-30.md` §2 is suspended pending re-scoping.

## What needs to happen next

### Path A — Seam-sufficiency audit (per `feedback_seam_sufficiency_audit`)

Compare two routers on the same real ledger rows:
- **Seam-only:** consumes only ComposedClaim seam fields + kill_pattern.
- **Raw-trace:** consumes seam + full Layer-1 verdict dict (kill_vector, step_trace, claim_payload).

If raw-trace router produces actionable routing deltas vs counters where seam-only doesn't, the seam is dropping the decisive information. Fix is to expand the seam schema.

### Path B — Layer-1 verdict richness audit

The 570 real rows are dominated by infrastructure-pending kps. Phase 1A's four retrofitted detectors (G02 WY, G10 BOCPD, G23 bootstrap, G11 MC G-test) are wired but only G10 has produced live results (the Salem cliff). Until more retrofitted detectors actually fire on real catalog data and populate the kill_ledger with rich kps, Layer 2 has nothing to navigate.

Concrete: run G02 WY, G23 bootstrap, G11 MC G-test against the real Mossinghoff catalog for an hour each; collect emissions; re-run Phase 3.0 with the enriched ledger.

### Path C — Counter-aware Layer 2 redesign

If the seam is sufficient AND Layer-1 verdicts are rich AND Layer 2 still ties counters, the Layer 2 PRIMITIVES need redesign. The motif extractor as designed (count (plugin, kp) co-occurrences) is structurally equivalent to a per-plugin counter. To produce decision-relevant signal counters can't, motifs would need to leverage cross-cell, cross-domain, or cross-time structure the counters don't see.

### Recommended single-iteration next step

Path B has the lowest risk and the highest information return: run a single iteration that produces ~50-100 live retrofitted Layer-1 verdicts on real Mahler catalog (the four Phase 1A detectors at thresholds known to fire), then re-run Phase 3.0. If the counter-baseline gap closes, Layer 2's value emerges as Layer 1 enriches. If not, Path A becomes the priority.

## Doctrinal posture

Per `feedback_failure_metabolization_doctrine` single phrase: *optimization consumes failure; Prometheus metabolizes failure.*

Phase 3.0 is a failure. It's the kind of failure the doctrine was built to metabolize: a real-data result that contradicts a synthetic-data verdict and forces the substrate to revise its priors. The substrate does not pause its lifecycle — it pauses ONE branch of work (BSD loader) to first run the audits that branch's premise depended on.

Per `feedback_instrument_vs_architectural_pass`: this is the conversion from "calibrated instrument" to "instrument pointed at something." The first time the instrument hit reality, reality said "your decisions don't depend on me yet."

The substrate continues. Next iteration is the Layer-1-enrichment retry. Phase 3.0 ran in 1 iteration and saved ~9 of misdirected effort. That's the cost-per-information the doctrine claims it's optimizing for.

---

**End Phase 3.0 verdict. ITER-56 closes. ITER-57 begins with Layer-1 verdict enrichment retry on real Mossinghoff catalog.**
