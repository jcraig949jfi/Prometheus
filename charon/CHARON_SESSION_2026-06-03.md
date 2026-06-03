# Charon Session — 2026-06-03

**First session in a month** (prior journal: 2026-05-03). The substrate moved without me: a full daemon swarm (acheron, erebos, hecate, lethe, moros, nephele, pollux, stygian) now lives under `charon/agents/`, and the live falsification thread is the **Erebos** Layer-1 + Seam + Layer-2 architecture (Phase 0 → Sprint-1 → Phase 3).

## What I walked into

The Erebos architectural arc as of 2026-05-30:
- Sprint-1: 10/10 PASS, reframed as instrument-calibration (synthetic, circular).
- Phase 3.0 (ITER-56): FAIL — original motif extractor == per-plugin counter, 0 deltas on real data.
- Phase 3.D (ITER-58): cross-cell primitive, "3 deltas vs per-plugin counter" → PASS.
- Phase 3.E (ITER-59): "2 deltas vs PAIR-AWARE counter" → "ROBUST PASS, lift filter load-bearing." Cited in EFG verdict §6 as the architecture's strongest real-data validation ("4 architectural passes").
- Stress audit (ITER-63/64/66): narrowed it — permutation null p=0.055 (borderline), scale-stress z dropped 2.48→1.92, HIERARCHICAL_ONLY.

## The one substrate-grade move I shipped

**Found the load-bearing gap:** every stress test in the audit (permutation null, scale stress, parent-child isolation) compared against `per_plugin_majority` — the WEAK unconditional counter (3 deltas). The architecture's *strongest* claim — 2 deltas vs the discriminating **pair-aware** counter — was reported as a raw count with **no permutation null at all.**

Built the missing null (`pair_aware_permutation_null.py`, Phase 3.K / ITER-83), mirroring the existing harness exactly so the only difference is the baseline. Results:
- **Pair-aware null:** observed 2, null mean 0.48, p95=2, **p=0.105** (7-seed mean 0.102, all ≥0.05) → STATISTICALLY UNDERDETERMINED.
- **Triplet null (ITER-84, inline):** observed 1 motif, null mean ~14, p(n≥obs)=1.00, ~90% of shuffles beat the observed lift → **observed BELOW null → FALSIFIED** (textbook lift inflation from low expected counts).
- **Cross-check:** the original per-plugin null decayed from p=0.055 to **p=0.075** on the grown ledger (699 rows) — confirms the scale-stress pattern a third way.

**Net: zero Erebos Layer-2 real-data signal claims survive a permutation null** (2 underdetermined, 1 falsified). Only the BSD infrastructure pass stands. Possibility C (doctrine's main claim wrong) now leads A/B.

Verdict: `pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md`.

## What I got right / the generalized lesson

The cargo-cult detector (`feedback_counter_baseline_discriminator`) fired correctly, but one level up: the verdict reported beating the discriminating baseline by *2 raw deltas* and called it ROBUST without testing whether 2 beats chance. Three harnesses made the same class of error — null-testing the convenient comparison, not the load-bearing one. **A "PASS vs baseline X" claim is not substrate-grade until it carries a permutation-null p-value vs that same X.** Filed as a candidate discipline primitive in the verdict §7.3.

## Honest residual (not a clean kill)

The pair-aware result sits exactly at null p95 — underdetermined, not slam-dunk null. The structural distinctions (joint vs marginal, lift-normalized vs raw) remain true; what collapses is the *statistical* claim of above-chance decision deltas. ITER-65 (lateral/organic data) is the one remaining path that could move the architecture back toward Possibility A.

## Standing recommendations for next session

1. **Re-frame the upstream docs.** `PHASE3_EFG_VERDICT` §6 and `STATE_AND_NEXT_STEPS` still say "4 architectural passes / robust against the strongest counter baseline." That language is now contradicted. Honest count: 0 signal passes survive a null, 1 infrastructure pass stands. (I did NOT edit those docs this session — left for a deliberate reframe pass.)
2. **Ship the discipline primitive** (verdict §7.3): counter-baseline smoke harnesses must emit their own permutation-null p-value or refuse to render PASS. This is the structural fix that prevents the whole class of error.
3. **ITER-65 lateral/organic data** is the decision point. If more data keeps weakening the signal (it has, three times now), the stand flips to Possibility C — pause + reopen doctrine.
4. **Cross-pollinate this verdict** before it drives a doctrine reopen — it's load-bearing. But note `feedback_llm_convergence_is_gravity_amplifier`: convergent frontier agreement that "the architecture is cargo cult" is a warning to investigate why the framing matches, not validation.

## Not pushed

Committed to main (per role convention; all agents commit direct). Did not push — awaiting authorization per standing orders.
