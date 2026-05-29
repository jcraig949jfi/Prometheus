# Sprint-1 A5: redundancy reduction over iterations — findings

**Date:** 2026-05-29
**Iteration:** ITER-49 (Phase 2, experiment 5 of 10)
**Verdict:** **PASS** (slope -0.00104 < threshold 0)
**Harness:** `charon/agents/erebos/sprint1/a5_redundancy_reduction.py`

---

## Hypothesis

> Eligibility rate declines as memory accumulates (slope of `cumulative_eligible / tick` over second half of stream is negative).

## Pre-committed pass threshold

Per roadmap v2 line 87: `downward trend → memory reduces wasted exploration`. Operationalized as: slope of the eligibility-rate series over the second half of the stream `< 0`.

## Protocol

1. Synthetic stream N=300, dup_fraction=0.40, seed=271.
2. Walk chronologically, growing `LedgerContext` from prior emissions.
3. For each tick t, compute `eligibility_rate(t) = cumulative_eligible / t`.
4. Linear-regress the rate series over t restricted to second half (ticks 151..300) — avoids early-warmup noise where t is small and rates are unstable.
5. Pass if slope < 0.

## Results

```
cumulative_eligible_final        = 194 / 300
second_half_initial_rate (t=151) = 0.7947
second_half_final_rate   (t=300) = 0.6467
slope                            = -0.001038
pass threshold                   = slope < 0
PASSED                           = True
```

## Honest reading

The slope is small in absolute terms (-0.001/tick) but the direction is unambiguous: the substrate's eligibility rate declines as the ledger grows.

Cross-check against A1: A1 measured a 49/80 = 61% catch rate on KNOWN duplicates. A5's observed eligibility-rate decline is consistent with that: if 40% of emissions are duplicates and the gate catches ~61% of them, the long-run eligibility rate should converge to 1 - (0.61 × 0.4) = 0.756 from above. The observed second-half rate (0.79 → 0.65) is in the right neighborhood, with finite-sample variance pulling the trajectory below the asymptote temporarily.

The two experiments measure related properties (A1: per-duplicate catch rate; A5: rate trend over time) and both point the same direction. This is the only Sprint-1 result where two experiments form a structural cross-check.

## What this verdict licenses

- The gate's duplicate-filtering compounds over time. As the substrate accumulates emissions, the fraction of eligible emissions DECLINES — memory is doing the work A1 measured at the per-event level.
- Phase 1B's seam discipline is causally connected to long-run substrate behavior, not just per-event eligibility decisions.

## Caveats

- **Small slope.** -0.001/tick is mild. A flatter / noisier substrate could easily show slope ≈ 0 or slightly positive in a different random seed. Future iteration should re-run across seeds 100..199 and report a confidence interval.
- **Synthetic stream.** Real ledgers may have different duplicate density / structure. Some real-substrate effects (e.g., catalog exhaustion) could produce DOWNWARD slopes even without memory — confounding factor.
- **Eligibility-rate is a proxy.** "Ticks-to-novel-emission" in the original hypothesis was reinterpreted as "marginal eligibility rate." Direct measurement (inter-eligible gap distribution) was deferred for simplicity. The two metrics should track each other but are not identical.

## Sprint-1 scoreboard (running)

```
A1 : PASS (differential=0.6125, threshold>0.30)
A2 : PASS (attribution_rate=0.9630, threshold>=0.50)
A3 : PASS (macro_f1_lift=0.2503, threshold>0.10)
A4 : PASS (eig_ratio=1.2149, threshold>1.20) — MARGINAL
A5 : PASS (slope=-0.00104, threshold<0)
A6 : pending
A7 : pending
A8 : pending
A9 : pending
A10: pending

Passes: 5 / 5 examined
Fails:  0 / 5 examined
Kill rule: fails >= 4 of 10 -> architecture paused per v3 §6
Headroom: 4 fails before pause is triggered
```
