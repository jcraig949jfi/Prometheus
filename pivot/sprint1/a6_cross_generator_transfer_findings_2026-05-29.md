# Sprint-1 A6: cross-generator transfer — findings

**Date:** 2026-05-29
**Iteration:** ITER-50 (Phase 2, experiment 6 of 10)
**Verdict:** **PASS** (lift 0.4133 > threshold 0.05)
**Harness:** `charon/agents/erebos/sprint1/a6_cross_generator_transfer.py`

---

## Hypothesis

> Kill_patterns generalize across generators (average pairwise transfer_rate exceeds shuffled-baseline by >5 percentage points).

## Pre-committed pass threshold

Per roadmap v2 line 88: `held-out predictive lift > 0`. Operationalized as `substrate_avg_transfer_rate - shuffled_baseline_avg > 0.05` (5 percentage points). The margin avoids declaring victory on a 0.001 improvement.

## Protocol

1. Synthetic ledger: 5 plugins × 30 input signatures = 150 emissions. Generative model: each input has a "ground-truth" kp; each plugin emits the truth with probability `P_KP_AGREE = 0.65`, else uniformly random.
2. Build a `KillTensor` with `plugin_id` in the DOMAIN slot and `input_signature` in the INVARIANT slot (via the default extractor).
3. For each (source_plugin, target_plugin) directed pair, run `predict_transfer` with `key_axes = (INVARIANT, KP)`. The pattern is `(input_signature, kp)` — input-conditional matching.
4. Average transfer_rate over all 20 directed pairs.
5. Baseline: shuffle the `kill_pattern` column across all rows (preserves marginals; breaks input → kp correlation). Recompute average.
6. Pass if `substrate_avg - baseline_avg > 0.05`.

## Results

```
substrate_avg_transfer_rate    = 0.5867
baseline_avg_transfer_rate     = 0.1733
lift                           = 0.4133
pass margin                    = 0.05
PASSED                         = True (margin: 0.3633)
```

## What went wrong (and how I fixed it)

The first run used `DEFAULT_TRANSFER_KEY_AXES = (PLUGIN, KP)`. Because plugin_id was in the DOMAIN slot and ALSO in the key, every plugin's patterns trivially didn't overlap with any other plugin's — transfer_rate = 0 across the board. Bug: the patterns must be plugin-independent for cross-plugin matching to be measurable.

Second run with `key_axes = (KP,)` flipped to the opposite degeneracy: every plugin has all 5 kps in its support set, so every (source, target) pair shows transfer_rate = 1.0 trivially. The set-membership of kps in each plugin's data is too coarse a comparison.

Third run (current) uses `key_axes = (INVARIANT, KP)` where INVARIANT = input_signature. Patterns are `(input_signature, kp)` pairs. Cross-plugin transfer fires when both plugins emitted the SAME kp for the SAME input. The shuffled baseline destroys that input-conditional correlation.

The fix wasn't a hyperparameter — it was a category error about what "pattern" should mean for a cross-generator test. Per `feedback_assume_wrong`, this is the kind of error worth documenting: even a well-architected primitive (cross_domain_transfer) needs the caller to think about what the comparison axis actually is.

## Honest reading

Lift of 0.413 is substantial — substrate's input-conditional kp agreement is ~3.4× the chance baseline. The generative model bakes a correlation of `P_KP_AGREE = 0.65` and the substrate detects most of it.

But the test is somewhat circular: I designed the data to have input-conditional correlation and verified the substrate detects it. Stronger evidence would come from running A6 on real ledger data where the correlation is not designed in. That follow-on is deferred.

The synthetic data does demonstrate that:
- `cross_domain_transfer` with `key_axes = (INVARIANT, KP)` is the correct primitive call for cross-plugin transfer.
- The substrate can detect ~3-4× lift over shuffled baseline at P_KP_AGREE=0.65.
- The result is robust to the directional asymmetries of `predict_transfer` (averaging over both directions).

## What this verdict licenses

- The `cross_domain_transfer` primitive (ITER-44) generalizes to cross-PLUGIN questions, not just cross-DOMAIN.
- When ground-truth correlation exists, the substrate's lift detection is well above pre-committed margin.
- A6 contributes a usable building block to Phase 3+ cross-plugin learning loops.

## Caveats

- **Designed correlation.** The 0.65 P_KP_AGREE is the strongest such caveat in Sprint-1 so far. The test verifies the substrate CAN detect input-conditional transfer; it does not test whether REAL ledger data exhibits it.
- **Single seed.** Re-run across seeds for confidence interval.
- **Key-axes selection is consequential.** Documented two failure modes (PLUGIN in key → 0 lift; KP only → 1.0 lift). Callers using `cross_domain_transfer` for plugin-axis questions must choose `key_axes = (INVARIANT, KP)` or equivalent.

## Sprint-1 scoreboard (running)

```
A1 : PASS (differential=0.6125, threshold>0.30)
A2 : PASS (attribution_rate=0.9630, threshold>=0.50)
A3 : PASS (macro_f1_lift=0.2503, threshold>0.10)
A4 : PASS (eig_ratio=1.2149, threshold>1.20) — MARGINAL
A5 : PASS (slope=-0.00104, threshold<0)
A6 : PASS (lift=0.4133, threshold>0.05)
A7 : pending
A8 : pending
A9 : pending
A10: pending

Passes: 6 / 6 examined
Fails:  0 / 6 examined
Kill rule: fails >= 4 of 10 -> architecture paused per v3 §6
Headroom: 4 fails before pause is triggered
```
