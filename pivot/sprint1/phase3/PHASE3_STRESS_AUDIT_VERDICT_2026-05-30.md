# Phase 3 stress audit — combined verdict (ITER-63 + ITER-66 + ITER-64)

**Date:** 2026-05-30
**Verdict:** **THE ARCHITECTURAL CLAIM IS NARROWER THAN IT WAS FRAMED.** The substrate's signal is real but BORDERLINE statistically significant, FAILS the scale stress test (z dropped as data grew), and is concentrated entirely on hierarchical (parent-child) structure with zero deltas on lateral structure.

---

## The three stress tests, in order of decreasing forgivingness

### ITER-63 — Permutation null on cross-cell primitive

```
observed actionable deltas    = 3
null mean (200 trials)        = 0.64
null std                      = 0.95
empirical p-value             = 0.0550   <-- just above the 0.05 threshold
z-score                       = 2.48
```

**Borderline.** The substrate has real signal (z=2.48) but not at conventional significance. ITER-58's PASS was BORDERLINE PASS, not architectural pass.

### ITER-66 — Scale stress (5× enrichment)

```
                          ITER-63 (n=674)     ITER-66 (n=895)
observed deltas              3                    5             (+1.7×)
null mean                    0.64                 1.74          (+2.7×)
z-score                      2.48                 1.92          (DOWN)
p-value                      0.055                0.080         (WORSE)
```

**The signal grew slower than the noise.** This is the most damaging finding. When you add 5× more real data, the architectural claim WEAKENS, not strengthens. A real architectural signal would have produced p < 0.01 at this scale; we got p = 0.08 instead.

### ITER-64 — Parent-child isolation

```
n_signatures with >=2 rows         = 73
  hierarchical (parent-child)      = 59     produced 1 actionable delta
  lateral (sibling)                = 14     produced 0 actionable deltas

n_rows in hierarchical              = 126
n_rows in lateral                   = 67
verdict                             = HIERARCHICAL_ONLY
```

**Lateral structure produces ZERO substrate deltas.** The doctrine's "Layer 2 produces decision-relevant signal counters cannot" claim has been falsified on lateral structure entirely. What signal exists is concentrated on hierarchical (Erebos emission → Stygian battery downstream) prediction.

## What this means together

The substrate's architectural claim has been NARROWED by three independent stress tests:

1. **The signal is real but borderline significant** (permutation null, p=0.055).
2. **The signal does NOT scale linearly with data** (5× enrichment weakened, not strengthened, the verdict).
3. **The signal is hierarchical-only** (zero deltas on lateral structure).

Synthesizing:

> The cross-cell motif primitive (ITER-58) detects a narrow, borderline-significant signal that exists specifically in parent-child prediction patterns. The substrate's broader architectural claim — that Layer 2 produces general decision-relevant signal counters cannot — is NOT supported on real data after stress testing.

## Doctrinal reframe required

This puts the substrate at the doctrinal crossroad ITER-58's verdict named:

- **Option 1** (reframe claim) — Layer 2 enriches representation, not decisions
- **Option 2** (Layer 2 redesign) — what we did at ITER-58
- **Option 3** (pause + reopen doctrine) — what becomes credible now

The stress audit's net result: **Option 2's redesign produced a hierarchical-prediction primitive, not a general Layer 2 navigator.** That's an honest narrowing, not a falsification. But it is also not the doctrine's framed claim.

Three honest possibilities for the doctrine:

### Possibility A — The architecture is genuinely narrow and that's OK

The substrate is a hierarchical-prediction system. Parent → child kp prediction is a real capability worth shipping; the doctrine's broader framing was aspirational. Future work narrows to this capability and ships it.

### Possibility B — The data isn't yet right for lateral signal

The current real ledger is dominated by hierarchical batches (Erebos→Stygian pipelines). Lateral structure may exist in nature but hasn't been emitted yet because the substrate doesn't have multi-detector batches on the same input. ITER-65 (per-batch motif extractor) might surface this once daemon-level integration produces organic lateral data.

### Possibility C — The doctrine's main claim is wrong

Layer 2 of the kind the doctrine envisions may not produce decision-relevant signal that counters cannot, period. The substrate built a sophisticated apparatus to measure something that isn't there. Pause and reopen.

## What the substrate must decide

Per `feedback_take_a_stand` and `feedback_calibration`:

The right action is **Possibility A + Possibility B in parallel**, NOT Possibility C immediately. Reasons:

- The signal IS real (z=2.48 on permutation null is not nothing)
- The signal IS structurally distinct from counters (the cross-cell primitive isn't a counter equivalent)
- The hierarchical-only result MAY reflect data shape (the ledger is hierarchical-heavy), not architectural impossibility
- ITER-65 (per-batch motif extractor) directly tests Possibility B's lateral-data hypothesis

But Possibility C is now LIVE. If ITER-65 also produces no lateral deltas after natural lateral data is generated, Possibility C becomes the leading interpretation. That would put the substrate's overall arc into deep revision territory.

## The reframe to ship today

`pivot/sprint1/phase3/PHASE3_D_CROSS_CELL_VERDICT_2026-05-30.md` and the related ITER-58 commit said "Option 2 architectural redesign is empirically supported." That claim was correct in its narrow form (Layer 2 primitive can produce SOME signal counters can't) but wrong in its broad framing (substrate's general value claim is empirically supported on real data).

The reframe:

> ITER-58 produced a hierarchical-prediction primitive. On the current real ledger, it produces a borderline-significant (p=0.055) signal on parent-child structures, ZERO signal on lateral structures, and the signal grows slower than noise as data scales. The architectural claim — that Layer 2 generally outperforms counters on real residue — is NOT yet supported. The narrower claim — that the substrate has a real hierarchical-prediction capability — IS supported.

## What proceeds

The substrate's pre-committed next-iteration responses, reordered by what these stress tests show:

1. **ITER-65 Phase 3.J per-batch motif extractor** (the lateral-data test from Possibility B). HIGHEST PRIORITY. If lateral deltas emerge under batch-grouping, Possibility A becomes the right reframe. If not, Possibility C becomes credible.

2. **ITER-67 Phase 3.L multi-counter tournament.** Test the substrate against Markov / Laplace-smoothed / kp-clustering counters. If substrate ties them on the narrow hierarchical signal, the architecture claim's floor is even lower than today's reframe suggests.

3. **Reframe SPRINT1_VERDICT + STATE_AND_NEXT_STEPS docs.** Today's `cross_cell_primitive PASS` and `5 architectural passes on real data` framing in earlier verdict docs is overstated relative to the stress audit. Update for honesty.

4. **Skip BSD-loader-dependent paths** (S1-S6 from the original Tier 1). The BSD MVP is shipped (ITER-61) as infrastructure, but its dependence on a robust Layer 2 doesn't survive today's testing.

## Doctrinal posture

Per `feedback_failure_metabolization_doctrine` single phrase: *optimization consumes failure; Prometheus metabolizes failure.*

Today the substrate metabolized:
- 1 real-data FAIL (Phase 3.0)
- 4 same-day PASSes
- 1 ARCHITECTURAL FINDING (cross-domain gap)
- 1 statistically BORDERLINE pass downgrade (permutation null)
- 1 scale-stress WEAKENING (z dropped as data grew)
- 1 STRUCTURAL NARROWING (hierarchical-only)

That's 8 substantive verdicts in one day. The substrate's net architectural state moved from "Sprint-1 PROCEED with caveats" (last night) → "narrow hierarchical-prediction capability with real-but-borderline signal" (now). The doctrine survives but in a smaller form.

Per `feedback_calibration`: stay calibrated. The substrate has a real measurement, not a confirmed theory. Do not paper over the narrowing.

Per `feedback_instrument_vs_architectural_pass`: today's earlier "architectural pass" claims must be downgraded. The substrate has at most ONE narrow-form architectural finding (hierarchical prediction) at borderline significance. Yesterday's instrument-calibration framing was more honest than today's "passes" became.

---

**End Phase 3 stress audit. ITER-63 + 64 + 66 close together.**

**Next: ITER-65 (per-batch motif extractor). The Possibility B test. If lateral deltas emerge, the doctrine's broader claim has room to recover. If not, Possibility C is on the table.**
