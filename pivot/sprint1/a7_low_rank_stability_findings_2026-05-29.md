# Sprint-1 A7: stable low-rank tensor structure — findings

**Date:** 2026-05-29
**Iteration:** ITER-51 (Phase 2, experiment 7 of 10)
**Verdict:** **PASS** (ratio 0.4658 < threshold 0.50) — marginal
**Harness:** `charon/agents/erebos/sprint1/a7_low_rank_stability.py`

---

## Hypothesis

> Kill tensor's new-cell discovery rate saturates: late growth is less than half of early growth.

## Pre-committed pass threshold

Per roadmap v2 line 89: `rank stabilizes (not linear in N) → real geometry, not duplicates`. Operationalized as `late_rate / early_rate < 0.5` over a 500-emission stream into a finite 360-cell space.

## Protocol

1. Stream N=500 synthetic emissions over a finite cell space: 4 plugins × 3 domains × 5 invariants × 6 kps = 360 cells.
2. Take `RankSnapshot` every 50 ticks (10 snapshots).
3. Compute `new_cells = n_populated(t) - n_populated(t-50)` between consecutive snapshots.
4. `early_rate = mean(first 2 deltas)`; `late_rate = mean(last 2 deltas)`.
5. Pass if `late_rate / early_rate < 0.5`.

## Results

```
n_snapshots             = 10
final_n_populated       = 271 / 360 cells (75%)
final_shape             = (4, 3, 5, 6) — full axis discovery
deltas (per 50 ticks)   = [37, 36, 33, 28, 22, 17, 17, 16, 18]
early_rate              = 36.5 new cells / 50 ticks
late_rate               = 17.0 new cells / 50 ticks
ratio                   = 0.4658
pass threshold          = ratio < 0.50
PASSED                  = True (margin: 0.0342)
```

## Honest reading — marginal pass

The ratio is below threshold but by less than 4 percentage points. Saturation is real (37 → 17 new cells per 50 ticks is a 54% reduction) but the curve hasn't flattened. The last three deltas (17, 16, 18) are essentially noise around 17 — indicating the substrate is still discovering ~17 new cells per 50 ticks at t=500.

Why not more saturated? 271/360 = 75% of the cell space is populated. With 25% of cells still empty, the iid uniform sampler can still find new cells. A longer run (N=2000) would push closer to full saturation.

The pass is real but the saturation is incomplete. Marginal — like A4.

## What this verdict licenses

- The kill_tensor's effective rank IS bounded — emissions saturate the cell space at the expected pace for an iid sampler over a finite structure.
- The substrate's rank-expansion primitive (ITER-43) correctly tracks this saturation.
- A flat tensor (no saturation) would have produced ratio ≈ 1.0; observed ratio 0.466 rules that out.

## Caveats

- **Marginal pass.** Margin 3.4 percentage points. A different seed could flip this near or just above 0.5.
- **iid uniform sampler.** Real substrate emissions are NOT uniform — plugins fire differentially, kp distributions are heavy-tailed. The saturation curve under real distributions could be steeper (faster saturation) or shallower (some cells unreachable).
- **75% saturation only.** The 360-cell space is not yet exhausted. A longer run would test whether the substrate truly low-rank or just under-sampled.
- **A6 cross-check unavailable.** The two experiments don't share a metric to cross-check; A6's lift and A7's saturation ratio are orthogonal.

## Sprint-1 scoreboard (running)

```
A1 : PASS (differential=0.6125, threshold>0.30)
A2 : PASS (attribution_rate=0.9630, threshold>=0.50)
A3 : PASS (macro_f1_lift=0.2503, threshold>0.10)
A4 : PASS (eig_ratio=1.2149, threshold>1.20) — MARGINAL
A5 : PASS (slope=-0.00104, threshold<0)
A6 : PASS (lift=0.4133, threshold>0.05)
A7 : PASS (ratio=0.4658, threshold<0.50) — MARGINAL
A8 : pending
A9 : pending
A10: pending

Passes: 7 / 7 examined
Fails:  0 / 7 examined
Marginal passes: 2 (A4, A7)
Kill rule: fails >= 4 of 10 -> architecture paused per v3 §6
Headroom: 4 fails before pause is triggered
```
