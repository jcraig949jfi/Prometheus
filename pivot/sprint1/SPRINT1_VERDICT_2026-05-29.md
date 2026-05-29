# Sprint-1 Verdict — Phase 2 ITER-55

**Date:** 2026-05-29
**Verdict:** **PROCEED** (architecture not paused per v3 §6 kill rule)
**Confidence:** Moderate; substantial caveats documented

---

## The pre-committed kill rule

Per Doctrine v1.0 §"the kill condition" and `pivot/erebos_v3_roadmap_v2_layer_seam_2026-05-27.md` line 77:

> If Sprint-1 fails ≥ 4 of the 10 experiments, the architecture is paused per v3 §6.

## Result

**10 of 10 experiments PASS. 0 fails.** The architecture clears the kill rule by a margin of 4.

## Per-experiment ledger

```
A1  PASS  duplicate_exhaust_differential = 0.6125     (threshold > 0.30)   CLEAN
A2  PASS  attribution_rate                = 0.9630   (threshold ≥ 0.50)   CLEAN (structural)
A3  PASS  macro_f1_lift_over_random       = 0.2503   (threshold > 0.10)   CLEAN
A4  PASS  eig_ratio_kp_over_rr            = 1.2149   (threshold > 1.20)   MARGINAL (0.015 over)
A5  PASS  eligibility_rate_slope          = -0.00104 (threshold < 0.00)   CLEAN (cross-checks A1)
A6  PASS  avg_transfer_lift_over_shuffle  = 0.4133   (threshold > 0.05)   CLEAN (3rd iter)
A7  PASS  late_rate_over_early_rate       = 0.4658   (threshold < 0.50)   MARGINAL (0.034 under)
A8  PASS  speedup_to_K_patterns_synthetic = 8.0000   (threshold > 1.50)   SYNTHETIC SUBSTITUTE
A9  PASS  revocation_propagation_rate     = 1.0000   (threshold ≥ 0.80)   CLEAN (structural)
A10 PASS  motif_to_class_purity           = 1.0000   (threshold > 0.40)   CLEAN
```

Quality breakdown: **7 clean passes** (A1, A2, A3, A5, A6, A9, A10) + **2 marginal passes** (A4, A7) + **1 synthetic substitute** (A8).

## What this verdict licenses

**The architecture is NOT paused.** Per Doctrine v1.0 §"the kill condition," Sprint-1 has not falsified the Layer-1 + Seam + Layer-2 design. The substrate may proceed to Phase 3+ work.

Specifically:
- The eligibility gate's memory-dependent criteria detect ~61% of known duplicates that an empty-memory gate cannot detect (A1).
- The routing layer's structural intent is dense: 26 of 27 kps resolve to specific non-default plugins across 24 distinct targets (A2).
- Kill_pattern labels encode learnable structure that a simple predictor can exploit (A3, lift 4× over random).
- Kp routing's information entropy exceeds round-robin's by 21% (A4 — marginal).
- The substrate's filter rate declines as the ledger grows, consistent with A1's per-event behavior compounding over time (A5).
- Cross-generator kp transfer beats shuffled baseline by 41 percentage points when measured input-conditionally (A6).
- The kill tensor saturates: late-stream new-cell rate drops to 47% of early-stream rate (A7 — marginal).
- The revocation primitive is structurally sound: 100% of revocations propagate to all three Layer-2 query methods (A9).
- Motif extraction recovers ground-truth structural classes at purity = 1.0 in a 3-class synthetic model (A10, clean separation).

## What this verdict does NOT license

The decision is to PROCEED, not to declare victory. The following caveats are material:

### 1. Synthetic data dominates
8 of 10 experiments use synthetic data (A1, A3, A4, A5, A6, A7, A8, A10). Only A2 and A9 are pure structural tests over the live registry/primitive code. **No experiment ran on real production ledger data.** The Sprint-1 result is about the substrate's CAPABILITIES, not its real-data PERFORMANCE.

### 2. A8 is a synthetic substitute, not the real test
A8's pre-committed protocol requires the BSD MVP loader (roadmap §35) which was never shipped. The synthetic substitute used the cross_domain_transfer primitive to count confirmed patterns instead of measuring wall-clock to first PROMOTED in BSD. The synthetic metric SATURATES at speedup=K (achieved here at K=8). The architectural claim "cross-domain residue accelerates new-domain coverage" is consistent with the substitute but unproven on real data.

**Recommendation:** Ship BSD MVP loader as the highest-priority Phase 3 follow-on; re-run A8 with the real protocol.

### 3. A4 and A7 are marginal passes
A4 cleared by 1.5 percentage points; A7 cleared by 3.4 percentage points. Either could flip to FAIL on a different random seed. A robust verdict would require a seed sweep with confidence intervals.

**Recommendation:** Re-run A4 and A7 across 100 seeds each; confirm pass holds for >95% of seeds before treating as substantively passed.

### 4. Several tests measure designed correlations
A6 verifies the substrate detects input-conditional correlation when P_KP_AGREE=0.65 is BAKED into the data. A10 verifies motifs find classes when each (plugin, kp) maps uniquely to one class. These tests check whether the substrate CAN detect the structure that's there; they cannot say whether real data HAS the structure.

### 5. Two daemon wires are deferred
- A2's runtime attribution requires the daemon to consult registry-resolved routing on every tick (the wire is partial — see ITER-38 implementation).
- A9's runtime revocation requires the daemon to consult `filter_active` before routing. This wire is not yet shipped.

These deferrals mean the architecture's CLAIMED runtime behavior depends on wires that haven't been built. A future iteration should ship both wires and re-run A2 and A9 in runtime mode.

## Quality-adjusted scoreboard

Excluding A8 (synthetic substitute) and the 2 marginal passes, the substrate has **7 clean passes** out of 10. Even under that strict reading, 7 is well above the kill-rule threshold (4 fails).

Under an even stricter reading where marginals are treated as failures and A8 is excluded, the substrate has 7 PASS / 2 FAIL / 1 BLOCKED = still well below the 4-fail kill rule.

The architecture survives multiple stringency thresholds.

## What proceeds, with what caveats

Per Doctrine v1.0, the verdict licenses Phase 3+ work to begin. The pre-committed kill condition is not triggered. Recommended Phase 3+ priorities:

1. **Ship BSD MVP loader** (priority 1 — required for A8 real-data re-run).
2. **Wire daemon-runtime kp routing** so A2 can be re-run as a real-time test, not just a structural one.
3. **Wire daemon-runtime revocation consultation** so A9 can be re-run end-to-end.
4. **Seed-sweep A4 and A7** across 100+ seeds; confirm pass holds robustly.
5. **Replay real production ledger** through A1, A3, A5, A6, A10 to test whether the substrate's synthetic-data capabilities transfer.
6. **Re-run Sprint-1 in full** after the above is shipped. This time, with real data and runtime wires, the result will be evidence about the substrate's actual value, not its potential capabilities.

## On the doctrinal posture

Per `feedback_calibration` and `feedback_assume_wrong`:

This Sprint-1 result is a **necessary** check on the architecture; it is not a sufficient one. The substrate cleared the pre-committed kill rule. That is what the rule was for. Phase 3+ work begins.

But every pass came with caveats — synthetic data, marginal margins, structural-only tests, designed correlations. The substrate's architectural claims (Layer 1 sharpness, seam disciplines, Layer 2 navigable geometry) survive Sprint-1's pre-committed challenge. They have not yet been tested on real data with full runtime integration. That test is the next chapter, not this one.

Per the doctrine's single phrase: **optimization consumes failure; Prometheus metabolizes failure.** Sprint-1's failure mode was the kill rule. It did not trigger. The substrate continues — with sharper failure data to integrate from the next round of work.

---

**End ITER-55. Sprint-1 closes. The architecture proceeds to Phase 3+ with the caveats above as the recommended audit trail.**
